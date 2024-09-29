function showAddPetForm() {
    var form = document.getElementById("addPetForm");
    form.style.display = (form.style.display === "none") ? "block" : "none";
}

// Fetch pets from the backend and populate the table
async function fetchPets() {
    try {
        const response = await fetch('/apis/add_pets');
        console.log('duma')
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const pets = await response.json();
        populateTable(pets);
    } catch (error) {
        console.error('Error fetching pets:', error);
    }
}

// Function to populate the pets table with data
function populateTable(pets) {
    const tableBody = document.querySelector('#petsTable tbody');
    tableBody.innerHTML = ''; // Clear existing rows

    pets.forEach(pet => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${pet.pet_name}</td>
            <td>${pet.pet_type}</td>
            <td>${pet.pet_age}</td>
            <td>
                <a href="{{ url_for('edit_pet', pet_id=pet.id) }}">Edit</a>
                <a href="{{ url_for('delete_pet', pet_id=pet.id) }}" onclick="return confirm('Are you sure you want to delete this pet?');">Delete</a>
            </td>

        `;
        tableBody.appendChild(row);
        console.log('Pet id:',pet.id)
    });
}

// Fetch pets when the page loads
window.onload = fetchPets;