# -*- coding: utf-8 -*-
"""
Copia de fotos legacy -> bucket de v2 (.scratch/migracion-datos-legacy/estructura-migracion.md §5).

Corre DENTRO del contenedor `app` de v2 (ya tiene boto3 + las credenciales de
escritura de v2 en el entorno, las mismas que usa `S3FotoStorage`). Las
credenciales de LECTURA del bucket legacy se pasan por variables de entorno
aparte (`LEGACY_AWS_ACCESS_KEY_ID`/`LEGACY_AWS_SECRET_ACCESS_KEY`/
`LEGACY_AWS_BUCKET`/`LEGACY_AWS_REGION`), nunca se escriben a disco.

Idempotente: la key de destino se deriva DETERMINÍSTICAMENTE del s3_key
legacy (mismo nombre de archivo, prefijo `legacy_`) -- si `PaqueteFoto.url`
ya contiene esa key, se salta sin volver a copiar.

Uso: DATABASE_URL ya está en el entorno del contenedor.
    python3 copiar_fotos.py --legacy-dir /tmp [--dry-run] [--limite N]
"""

import argparse
import json
import os
import sys

import boto3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limite", type=int, default=None)
    args = ap.parse_args()

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.domain.paquete import Paquete
    from app.domain.paquete_foto import PaqueteFoto

    engine = create_engine(os.environ["DATABASE_URL"])
    db = sessionmaker(bind=engine)()

    legacy_client = boto3.client(
        "s3",
        region_name=os.environ.get("LEGACY_AWS_REGION", "us-east-1"),
        aws_access_key_id=os.environ["LEGACY_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["LEGACY_AWS_SECRET_ACCESS_KEY"],
    )
    legacy_bucket = os.environ["LEGACY_AWS_BUCKET"]

    v2_bucket = os.environ["AWS_S3_BUCKET_NAME"]
    v2_region = os.environ.get("AWS_REGION", "us-east-1")
    v2_prefix = os.environ.get("AWS_S3_PREFIX_FOTOS", "paquetes-recibidos-imagenes/")
    v2_client = boto3.client(
        "s3",
        region_name=v2_region,
        aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY_ID") or None,
        aws_secret_access_key=os.environ.get("AWS_S3_SECRET_ACCESS_KEY") or None,
    )

    with open(os.path.join(args.legacy_dir, "file_uploads.json"), encoding="utf-8") as f:
        fotos = json.load(f) or []
    if args.limite:
        fotos = fotos[: args.limite]

    # Cache de Paquete.id por access_code, para no re-consultar por cada foto.
    paquete_id_por_codigo = {}

    reporte = {"copiadas": 0, "saltadas_ya_existe": 0, "sin_paquete": 0, "errores": []}

    for foto in fotos:
        tracking = foto["tracking_number"]
        s3_key_legacy = foto["s3_key"]
        nombre_archivo = s3_key_legacy.rsplit("/", 1)[-1]
        key_destino = f"{v2_prefix}legacy_{nombre_archivo}"
        url_destino = f"https://{v2_bucket}.s3.{v2_region}.amazonaws.com/{key_destino}"

        paquete_id = paquete_id_por_codigo.get(tracking)
        if paquete_id is None:
            p = db.query(Paquete).filter(Paquete.access_code == tracking).one_or_none()
            if p is None:
                reporte["sin_paquete"] += 1
                continue
            paquete_id = p.id
            paquete_id_por_codigo[tracking] = paquete_id

        ya_existe = db.query(PaqueteFoto).filter(PaqueteFoto.url == url_destino).one_or_none()
        if ya_existe:
            reporte["saltadas_ya_existe"] += 1
            continue

        if args.dry_run:
            reporte["copiadas"] += 1
            continue

        try:
            obj = legacy_client.get_object(Bucket=legacy_bucket, Key=s3_key_legacy)
            contenido = obj["Body"].read()
            content_type = obj.get("ContentType", "image/webp")
            v2_client.put_object(
                Bucket=v2_bucket, Key=key_destino, Body=contenido,
                ContentType=content_type, ACL="public-read",
            )
            db.add(PaqueteFoto(paquete_id=paquete_id, url=url_destino))
            db.flush()
            reporte["copiadas"] += 1
        except Exception as exc:  # noqa: BLE001 -- reporte agregado, no debe frenar el loop
            reporte["errores"].append(f"{tracking}/{nombre_archivo}: {exc}")

        if reporte["copiadas"] % 200 == 0 and reporte["copiadas"] > 0 and not args.dry_run:
            db.commit()
            print(f"...{reporte['copiadas']} copiadas hasta ahora", file=sys.stderr)

    if args.dry_run:
        db.rollback()
        print("=== DRY RUN -- nada se escribió ===")
    else:
        db.commit()
        print("=== Cambios confirmados (commit) ===")

    print(json.dumps(reporte, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
