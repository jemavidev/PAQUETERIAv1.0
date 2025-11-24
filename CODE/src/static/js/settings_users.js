// Funciones para gestión de usuarios en Settings

// Funciones para modales
function openCreateUserModal() {
    document.getElementById('createUserModal').classList.remove('hidden');
    document.getElementById('createUserForm').reset();
}

function closeCreateUserModal() {
    document.getElementById('createUserModal').classList.add('hidden');
}

function editUser(userId, username, email, fullName, phone, role, isActive) {
    const cleanUserId = String(userId).trim();
    document.getElementById('edit_user_id').value = cleanUserId;
    document.getElementById('edit_username').value = username || '';
    document.getElementById('edit_email').value = email || '';
    document.getElementById('edit_full_name').value = fullName || '';
    document.getElementById('edit_phone').value = phone || '';
    document.getElementById('edit_role').value = role || 'OPERADOR';
    const isActiveBool = isActive === true || isActive === 'True' || isActive === 'true' || String(isActive).toLowerCase() === 'true';
    document.getElementById('edit_is_active').checked = isActiveBool;
    document.getElementById('editUserModal').classList.remove('hidden');
}

function closeEditUserModal() {
    document.getElementById('editUserModal').classList.add('hidden');
}

function activateUser(userId, username) {
    if (confirm(`¿Activar usuario "${username}"?`)) {
        fetch('/api/admin/users/toggle-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: String(userId) })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success !== false) {
                    showSuccessMessage('Usuario activado');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Error: ' + (data.detail || data.message));
                }
            })
            .catch(err => alert('Error de conexión'));
    }
}

function deactivateUser(userId, username) {
    if (confirm(`¿Desactivar usuario "${username}"?`)) {
        fetch('/api/admin/users/toggle-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id: String(userId) })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success !== false) {
                    showSuccessMessage('Usuario desactivado');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Error: ' + (data.detail || data.message));
                }
            })
            .catch(err => alert('Error de conexión'));
    }
}

// Búsqueda de usuarios
function searchUsers() {
    const input = document.getElementById('userSearchInput');
    const filter = input.value.toUpperCase();
    const table = document.getElementById('usersTable');
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        const td = tr[i].getElementsByTagName('td');
        let found = false;
        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        tr[i].style.display = found ? '' : 'none';
    }
}

function clearSearch() {
    document.getElementById('userSearchInput').value = '';
    searchUsers();
}

function showSuccessMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 bg-green-500';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Manejar formularios
document.addEventListener('DOMContentLoaded', function () {
    // Formulario crear usuario
    const createForm = document.getElementById('createUserForm');
    if (createForm) {
        createForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const jsonData = {};
            for (let [key, value] of formData.entries()) {
                jsonData[key] = value;
            }

            try {
                const response = await fetch('/api/admin/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(jsonData)
                });

                const result = await response.json();
                if (response.ok) {
                    closeCreateUserModal();
                    showSuccessMessage('Usuario creado');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Error: ' + (result.detail || 'Error desconocido'));
                }
            } catch (error) {
                alert('Error de conexión');
            }
        });
    }

    // Formulario editar usuario
    const editForm = document.getElementById('editUserForm');
    if (editForm) {
        editForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const jsonData = {};
            for (let [key, value] of formData.entries()) {
                if (key === 'user_id') {
                    jsonData[key] = String(value).trim();
                } else {
                    jsonData[key] = value;
                }
            }

            if (!formData.has('is_active')) {
                jsonData['is_active'] = false;
            } else {
                jsonData['is_active'] = jsonData['is_active'] === 'on' || jsonData['is_active'] === 'true';
            }

            try {
                const response = await fetch('/api/admin/users/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(jsonData)
                });

                const result = await response.json();
                if (response.ok && result.success !== false) {
                    closeEditUserModal();
                    showSuccessMessage('Usuario actualizado');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Error: ' + (result.detail || result.message || 'Error desconocido'));
                }
            } catch (error) {
                alert('Error de conexión');
            }
        });
    }
});
