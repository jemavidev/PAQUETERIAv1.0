"""
CUFE/CUDE Validation Test Suite
================================
Comprehensive validation of CUFE/CUDE extraction from PDFs, XMLs, and cross-file consistency.

CUFE Specification:
- Length: 96 characters
- Format: Hexadecimal (0-9, a-f)
- No spaces allowed
- Unique identifier for each electronic invoice
- Filenames are the CUFE codes
"""

import os
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of extracting data from a file"""
    file_path: str
    file_type: str  # 'pdf', 'xml'
    cufe: Optional[str] = None
    cufe_valid: bool = False
    vendor_nit: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_city: Optional[str] = None
    buyer_nit: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_city: Optional[str] = None
    issue_date: Optional[str] = None
    document_number: Optional[str] = None
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    subtotal_amount: Optional[float] = None
    line_count: Optional[int] = None
    extraction_errors: List[str] = None
    software_provider: Optional[str] = None
    pdf_format_type: Optional[str] = None  # Type of PDF vendor
    xml_namespace: Optional[str] = None
    qr_code_url: Optional[str] = None

    def __post_init__(self):
        if self.extraction_errors is None:
            self.extraction_errors = []


class CufeValidator:
    """Validates CUFE/CUDE format and extraction"""

    CUFE_PATTERN = re.compile(r'^[a-f0-9]{96}$', re.IGNORECASE)
    CUFE_LENGTH = 96

    @classmethod
    def is_valid_format(cls, cufe: str) -> Tuple[bool, str]:
        """
        Validate CUFE format

        Returns:
            (is_valid, error_message)
        """
        if not cufe:
            return False, "CUFE is empty"

        if ' ' in cufe:
            return False, f"CUFE contains spaces: '{cufe}'"

        if len(cufe) != cls.CUFE_LENGTH:
            return False, f"CUFE length is {len(cufe)}, expected {cls.CUFE_LENGTH}"

        if not cls.CUFE_PATTERN.match(cufe):
            return False, f"CUFE contains invalid characters (must be hex): {cufe}"

        return True, "CUFE format is valid"

    @classmethod
    def extract_from_filename(cls, filename: str) -> Optional[str]:
        """Extract CUFE from filename (without extension)"""
        name = Path(filename).stem
        if cls.CUFE_PATTERN.match(name):
            return name.lower()
        return None


class XMLExtractor:
    """Extract data from DIAN XML files"""

    NAMESPACES = {
        'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    }

    @classmethod
    def extract(cls, file_path: str) -> ExtractionResult:
        """Extract invoice data from XML file"""
        result = ExtractionResult(file_path=file_path, file_type='xml')

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract namespace from root element
            if '}' in root.tag:
                namespace = root.tag.split('}')[0][1:]
                result.xml_namespace = namespace

            # Extract CUFE from UUID element
            uuid_elem = root.find('.//cbc:UUID', cls.NAMESPACES)
            if uuid_elem is not None and uuid_elem.text:
                cufe = uuid_elem.text.strip().lower()
                result.cufe = cufe
                result.cufe_valid, _ = CufeValidator.is_valid_format(cufe)

            # Extract document number
            id_elem = root.find('.//cbc:ID', cls.NAMESPACES)
            if id_elem is not None:
                result.document_number = id_elem.text

            # Extract issue date
            date_elem = root.find('.//cbc:IssueDate', cls.NAMESPACES)
            if date_elem is not None:
                result.issue_date = date_elem.text

            # Extract vendor info
            vendor_party = root.find('.//cac:AccountingSupplierParty', cls.NAMESPACES)
            if vendor_party is not None:
                # Vendor NIT
                nit_elem = vendor_party.find('.//cbc:CompanyID', cls.NAMESPACES)
                if nit_elem is not None:
                    result.vendor_nit = nit_elem.text

                # Vendor name
                name_elem = vendor_party.find('.//cbc:RegistrationName', cls.NAMESPACES)
                if name_elem is not None:
                    result.vendor_name = name_elem.text

                # Vendor address
                address_elem = vendor_party.find('.//cac:AddressLine/cbc:Line', cls.NAMESPACES)
                if address_elem is not None:
                    result.vendor_address = address_elem.text

                # Vendor city
                city_elem = vendor_party.find('.//cbc:CityName', cls.NAMESPACES)
                if city_elem is not None:
                    result.vendor_city = city_elem.text

            # Extract buyer info
            buyer_party = root.find('.//cac:AccountingCustomerParty', cls.NAMESPACES)
            if buyer_party is not None:
                # Buyer NIT
                nit_elem = buyer_party.find('.//cbc:CompanyID', cls.NAMESPACES)
                if nit_elem is not None:
                    result.buyer_nit = nit_elem.text

                # Buyer name
                name_elem = buyer_party.find('.//cbc:RegistrationName', cls.NAMESPACES)
                if name_elem is not None:
                    result.buyer_name = name_elem.text

                # Buyer address
                address_elem = buyer_party.find('.//cac:AddressLine/cbc:Line', cls.NAMESPACES)
                if address_elem is not None:
                    result.buyer_address = address_elem.text

                # Buyer city
                city_elem = buyer_party.find('.//cbc:CityName', cls.NAMESPACES)
                if city_elem is not None:
                    result.buyer_city = city_elem.text

            # Extract financial totals
            legal_total = root.find('.//cac:LegalMonetaryTotal', cls.NAMESPACES)
            if legal_total is not None:
                total_elem = legal_total.find('.//cbc:PayableAmount', cls.NAMESPACES)
                if total_elem is not None and total_elem.text:
                    result.total_amount = float(total_elem.text)

                subtotal_elem = legal_total.find('.//cbc:TaxExclusiveAmount', cls.NAMESPACES)
                if subtotal_elem is not None and subtotal_elem.text:
                    result.subtotal_amount = float(subtotal_elem.text)

            # Extract tax total
            tax_total = root.find('.//cac:TaxTotal', cls.NAMESPACES)
            if tax_total is not None:
                tax_elem = tax_total.find('.//cbc:TaxAmount', cls.NAMESPACES)
                if tax_elem is not None and tax_elem.text:
                    result.tax_amount = float(tax_elem.text)

            # Count invoice lines
            lines = root.findall('.//cac:InvoiceLine', cls.NAMESPACES)
            result.line_count = len(lines)

            # Extract software provider
            software_provider = root.find('.//sts:SoftwareProvider/sts:ProviderID', cls.NAMESPACES)
            if software_provider is not None:
                result.software_provider = software_provider.text

            # Extract QR code URL
            qr_elem = root.find('.//sts:QRCode', cls.NAMESPACES)
            if qr_elem is not None:
                result.qr_code_url = qr_elem.text

        except ET.ParseError as e:
            result.extraction_errors.append(f"XML parse error: {str(e)}")
        except Exception as e:
            result.extraction_errors.append(f"Unexpected error: {str(e)}")

        return result


class PDFExtractor:
    """Extract data from PDF files using simple text extraction"""

    @classmethod
    def extract(cls, file_path: str) -> ExtractionResult:
        """
        Extract data from PDF file.

        Note: Full PDF parsing requires pdfplumber or similar.
        This version provides structure for future implementation.
        """
        result = ExtractionResult(file_path=file_path, file_type='pdf')

        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                # Extract basic document info
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text() or ""

                    # Try to detect software provider from text
                    if 'dian' in first_page_text.lower():
                        result.pdf_format_type = 'DIAN'
                    elif 'certificado' in first_page_text.lower():
                        result.pdf_format_type = 'VENDOR'

                    # Extract dates (simple pattern matching)
                    date_pattern = r'(\d{4}-\d{2}-\d{2})'
                    dates = re.findall(date_pattern, first_page_text)
                    if dates:
                        result.issue_date = dates[0]

        except ImportError:
            result.extraction_errors.append("pdfplumber not available")
        except Exception as e:
            result.extraction_errors.append(f"PDF extraction error: {str(e)}")

        return result


class CufeValidationTest:
    """Test suite for CUFE validation"""

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.cufe_dir = os.path.join(base_path, 'CUFE')
        self.cufe_xml_dir = os.path.join(base_path, 'CUFE-XML')
        self.facturas_dir = os.path.join(base_path, 'FACTURAS')

        self.results = {
            'CUFE': [],
            'CUFE-XML': [],
            'FACTURAS': []
        }

        self.cufe_map = defaultdict(dict)  # cufe -> {folder -> result}

    def test_extraction_from_pdf_filename(self) -> Dict:
        """Test CUFE extraction from PDF filenames"""
        logger.info("Testing CUFE extraction from PDF filenames...")

        results = {'success': 0, 'failed': 0, 'samples': []}

        for folder_key in ['CUFE', 'CUFE-XML', 'FACTURAS']:
            folder_path = getattr(self, f'{folder_key.lower()}_dir'.replace('-', '_'))
            if not os.path.exists(folder_path):
                continue

            pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

            for pdf_file in pdf_files:
                cufe = CufeValidator.extract_from_filename(pdf_file)
                if cufe:
                    results['success'] += 1
                    if results['success'] <= 3:
                        results['samples'].append({
                            'file': pdf_file,
                            'cufe': cufe,
                            'folder': folder_key
                        })
                else:
                    results['failed'] += 1

        logger.info(f"Filename extraction: {results['success']} success, {results['failed']} failed")
        return results

    def test_extraction_from_xml(self) -> Dict:
        """Test CUFE extraction from XML files"""
        logger.info("Testing CUFE extraction from XML files...")

        results = {'success': 0, 'failed': 0, 'samples': []}
        errors = []

        if not os.path.exists(self.cufe_xml_dir):
            return results

        xml_files = [f for f in os.listdir(self.cufe_xml_dir) if f.endswith('.xml')]

        for xml_file in xml_files:
            file_path = os.path.join(self.cufe_xml_dir, xml_file)
            result = XMLExtractor.extract(file_path)

            if result.cufe and result.cufe_valid:
                results['success'] += 1
                if results['success'] <= 3:
                    results['samples'].append({
                        'file': xml_file,
                        'cufe': result.cufe,
                        'vendor': result.vendor_name
                    })
            else:
                results['failed'] += 1
                if result.extraction_errors:
                    errors.extend(result.extraction_errors[:1])

            self.results['CUFE-XML'].append(result)

        if errors:
            logger.warning(f"XML extraction errors: {errors[:3]}")

        logger.info(f"XML extraction: {results['success']} success, {results['failed']} failed")
        return results

    def test_cufe_format_validation(self) -> Dict:
        """Test CUFE format validation (96 chars, hex, no spaces)"""
        logger.info("Testing CUFE format validation...")

        results = {
            'valid_format': 0,
            'invalid_length': 0,
            'contains_spaces': 0,
            'invalid_characters': 0,
            'empty': 0
        }

        for folder_key in ['CUFE', 'CUFE-XML', 'FACTURAS']:
            for result in self.results[folder_key]:
                if not result.cufe:
                    results['empty'] += 1
                    continue

                is_valid, error_msg = CufeValidator.is_valid_format(result.cufe)

                if is_valid:
                    results['valid_format'] += 1
                else:
                    if 'spaces' in error_msg:
                        results['contains_spaces'] += 1
                    elif 'length' in error_msg:
                        results['invalid_length'] += 1
                    elif 'invalid characters' in error_msg:
                        results['invalid_characters'] += 1

        logger.info(f"Format validation: {results['valid_format']} valid")
        return results

    def test_pdf_xml_matching(self) -> Dict:
        """Test that corresponding PDF and XML files have matching CUFEs"""
        logger.info("Testing PDF-XML CUFE matching...")

        results = {
            'matched': 0,
            'mismatched': 0,
            'xml_only': 0,
            'pdf_only': 0,
            'mismatches': []
        }

        # Build maps by CUFE
        xml_cufes = {}
        pdf_cufes = {}

        for result in self.results['CUFE-XML']:
            if result.cufe and result.file_type == 'xml':
                xml_cufes[result.cufe] = result

        for result in self.results['CUFE-XML']:
            if result.cufe and result.file_type == 'pdf':
                pdf_cufes[result.cufe] = result

        # Check matching
        all_cufes = set(xml_cufes.keys()) | set(pdf_cufes.keys())

        for cufe in all_cufes:
            if cufe in xml_cufes and cufe in pdf_cufes:
                results['matched'] += 1
            elif cufe in xml_cufes:
                results['xml_only'] += 1
                results['mismatches'].append({'cufe': cufe, 'status': 'xml_only'})
            else:
                results['pdf_only'] += 1
                results['mismatches'].append({'cufe': cufe, 'status': 'pdf_only'})

        logger.info(f"PDF-XML matching: {results['matched']} matched, "
                   f"{results['xml_only']} XML-only, {results['pdf_only']} PDF-only")

        return results

    def test_data_extraction_coherence(self) -> Dict:
        """Test that extracted data is coherent and complete"""
        logger.info("Testing data extraction coherence...")

        results = {
            'complete': 0,
            'partial': 0,
            'errors': 0,
            'sample_data': []
        }

        for result in self.results['CUFE-XML']:
            if result.extraction_errors:
                results['errors'] += 1
                continue

            # Check if key fields are populated
            key_fields = [
                result.vendor_nit,
                result.vendor_name,
                result.buyer_nit,
                result.buyer_name,
                result.issue_date
            ]

            populated_count = sum(1 for f in key_fields if f)

            if populated_count == 5:
                results['complete'] += 1
                if len(results['sample_data']) < 3:
                    results['sample_data'].append({
                        'file': result.file_path.split('/')[-1],
                        'vendor': result.vendor_name,
                        'buyer': result.buyer_name,
                        'date': result.issue_date
                    })
            else:
                results['partial'] += 1

        logger.info(f"Data coherence: {results['complete']} complete, "
                   f"{results['partial']} partial, {results['errors']} with errors")

        return results

    def test_vendor_variation_detection(self) -> Dict:
        """Detect different vendors and software providers"""
        logger.info("Testing vendor variation detection...")

        vendor_counter = Counter()
        software_counter = Counter()
        vendor_details = {}

        for result in self.results['CUFE-XML']:
            if result.vendor_name:
                vendor_counter[result.vendor_name] += 1
                if result.vendor_name not in vendor_details:
                    vendor_details[result.vendor_name] = {
                        'nit': result.vendor_nit,
                        'city': result.vendor_city,
                        'count': 0
                    }
                vendor_details[result.vendor_name]['count'] += 1

            if result.software_provider:
                software_counter[result.software_provider] += 1

        results = {
            'unique_vendors': len(vendor_counter),
            'unique_software_providers': len(software_counter),
            'top_vendors': vendor_counter.most_common(10),
            'vendor_details': vendor_details,
            'software_providers': dict(software_counter)
        }

        logger.info(f"Variations found: {results['unique_vendors']} vendors, "
                   f"{results['unique_software_providers']} software providers")

        return results

    def test_date_range_analysis(self) -> Dict:
        """Analyze date range of documents"""
        logger.info("Testing date range analysis...")

        dates = []
        for result in self.results['CUFE-XML']:
            if result.issue_date:
                try:
                    datetime.fromisoformat(result.issue_date)
                    dates.append(result.issue_date)
                except:
                    pass

        if not dates:
            return {
                'min_date': None,
                'max_date': None,
                'total_dated': 0,
                'total_undated': sum(1 for r in self.results['CUFE-XML'] if not r.issue_date)
            }

        dates.sort()

        results = {
            'min_date': dates[0],
            'max_date': dates[-1],
            'total_dated': len(dates),
            'total_undated': sum(1 for r in self.results['CUFE-XML'] if not r.issue_date),
            'date_distribution': self._count_dates_by_month(dates)
        }

        logger.info(f"Date range: {results['min_date']} to {results['max_date']}")

        return results

    @staticmethod
    def _count_dates_by_month(dates: List[str]) -> Dict:
        """Count documents by month"""
        month_counter = Counter()
        for date in dates:
            try:
                month = date[:7]  # YYYY-MM
                month_counter[month] += 1
            except:
                pass
        return dict(month_counter)

    def test_totals_calculation(self) -> Dict:
        """Test financial totals consistency"""
        logger.info("Testing financial totals calculation...")

        results = {
            'total_by_folder': {},
            'with_tax': 0,
            'with_subtotal': 0,
            'sample_amounts': []
        }

        for folder_key in ['CUFE-XML', 'FACTURAS']:
            total_sum = 0
            count = 0

            for result in self.results[folder_key]:
                if result.total_amount:
                    total_sum += result.total_amount
                    count += 1
                    if len(results['sample_amounts']) < 5:
                        results['sample_amounts'].append({
                            'file': result.file_path.split('/')[-1],
                            'total': result.total_amount,
                            'tax': result.tax_amount,
                            'subtotal': result.subtotal_amount
                        })

            if result.tax_amount:
                results['with_tax'] += 1
            if result.subtotal_amount:
                results['with_subtotal'] += 1

            results['total_by_folder'][folder_key] = {
                'sum': total_sum,
                'count': count,
                'avg': total_sum / count if count > 0 else 0
            }

        logger.info(f"Totals analysis: {results['with_tax']} docs with tax data")

        return results

    def run_full_validation_suite(self) -> Dict:
        """Run complete validation suite"""
        logger.info("=" * 80)
        logger.info("CUFE VALIDATION SUITE - STARTING")
        logger.info("=" * 80)

        # Scan directories and extract data
        self._scan_and_extract_all()

        # Run all tests
        test_results = {
            'filename_extraction': self.test_extraction_from_pdf_filename(),
            'xml_extraction': self.test_extraction_from_xml(),
            'format_validation': self.test_cufe_format_validation(),
            'pdf_xml_matching': self.test_pdf_xml_matching(),
            'data_coherence': self.test_data_extraction_coherence(),
            'vendor_variations': self.test_vendor_variation_detection(),
            'date_range': self.test_date_range_analysis(),
            'totals': self.test_totals_calculation()
        }

        # Compile summary
        summary = self._compile_summary(test_results)

        logger.info("=" * 80)
        logger.info("CUFE VALIDATION SUITE - COMPLETE")
        logger.info("=" * 80)

        return {
            'summary': summary,
            'test_results': test_results,
            'metadata': {
                'execution_date': datetime.now().isoformat(),
                'base_path': self.base_path
            }
        }

    def _scan_and_extract_all(self):
        """Scan all directories and extract data"""
        logger.info("Scanning directories and extracting data...")

        # CUFE folder (PDFs only)
        self._scan_folder(self.cufe_dir, 'CUFE', file_types=['pdf'])

        # CUFE-XML folder (XMLs and PDFs)
        self._scan_folder(self.cufe_xml_dir, 'CUFE-XML', file_types=['xml', 'pdf'])

        # FACTURAS folder (PDFs only)
        self._scan_folder(self.facturas_dir, 'FACTURAS', file_types=['pdf'])

    def _scan_folder(self, folder_path: str, folder_key: str, file_types: List[str]):
        """Scan a folder and extract data"""
        if not os.path.exists(folder_path):
            logger.warning(f"Folder not found: {folder_path}")
            return

        logger.info(f"Scanning {folder_key} folder...")

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if filename.endswith('.xml'):
                if 'xml' in file_types:
                    result = XMLExtractor.extract(file_path)
                    self.results[folder_key].append(result)
            elif filename.endswith('.pdf'):
                if 'pdf' in file_types:
                    result = PDFExtractor.extract(file_path)
                    # Extract CUFE from filename
                    cufe = CufeValidator.extract_from_filename(filename)
                    if cufe:
                        result.cufe = cufe
                        result.cufe_valid, _ = CufeValidator.is_valid_format(cufe)
                    self.results[folder_key].append(result)

    def _compile_summary(self, test_results: Dict) -> Dict:
        """Compile overall summary statistics"""
        total_files = sum(len(results) for results in self.results.values())
        total_cufes_extracted = sum(
            1 for results in self.results.values()
            for r in results
            if r.cufe
        )

        valid_cufes = sum(
            1 for results in self.results.values()
            for r in results
            if r.cufe_valid
        )

        success_rate = (valid_cufes / total_files * 100) if total_files > 0 else 0

        return {
            'total_files': total_files,
            'total_cufes_extracted': total_cufes_extracted,
            'total_cufes_valid': valid_cufes,
            'extraction_success_rate': f"{success_rate:.1f}%",
            'by_folder': {
                folder: {
                    'total_files': len(results),
                    'with_cufe': sum(1 for r in results if r.cufe),
                    'valid_cufe': sum(1 for r in results if r.cufe_valid),
                    'errors': sum(len(r.extraction_errors) for r in results)
                }
                for folder, results in self.results.items()
            }
        }


def generate_json_report(full_results: Dict, output_path: str):
    """Generate JSON report"""

    # Convert dataclass results to dicts for JSON serialization
    def convert_results(results_dict):
        converted = {}
        for key, results_list in results_dict.items():
            converted[key] = {
                'total': len(results_list),
                'errors': [],
                'extracted': []
            }

            for result in results_list:
                if result.extraction_errors:
                    converted[key]['errors'].append({
                        'file': result.file_path.split('/')[-1],
                        'errors': result.extraction_errors
                    })
                else:
                    # Only include non-None values
                    extracted = {k: v for k, v in asdict(result).items()
                                if v is not None and k != 'extraction_errors'}
                    converted[key]['extracted'].append(extracted)

        return converted

    report = {
        'summary': full_results['summary'],
        'by_folder': convert_results(full_results['test_results'].get('test_results', {})),
        'test_details': {
            'filename_extraction': full_results['test_results']['filename_extraction'],
            'xml_extraction': full_results['test_results']['xml_extraction'],
            'format_validation': full_results['test_results']['format_validation'],
            'pdf_xml_matching': {
                k: v for k, v in full_results['test_results']['pdf_xml_matching'].items()
                if k != 'mismatches' or len(v) <= 10
            },
            'data_coherence': full_results['test_results']['data_coherence'],
            'vendor_variations': {
                'unique_vendors': full_results['test_results']['vendor_variations']['unique_vendors'],
                'unique_software_providers': full_results['test_results']['vendor_variations']['unique_software_providers'],
                'top_vendors': [{'name': name, 'count': count}
                              for name, count in full_results['test_results']['vendor_variations']['top_vendors']],
            },
            'date_range': full_results['test_results']['date_range'],
            'totals': full_results['test_results']['totals']
        },
        'metadata': full_results['metadata']
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Report saved to: {output_path}")


if __name__ == '__main__':
    base_path = '/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE'

    # Run validation suite
    validator = CufeValidationTest(base_path)
    results = validator.run_full_validation_suite()

    # Generate report
    report_path = '/home/stk/Documents/GIT/PAQUETEX v1.0/cufe_validation_report.json'
    generate_json_report(results, report_path)

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(json.dumps(results['summary'], indent=2))
    print(f"\nFull report saved to: {report_path}")
