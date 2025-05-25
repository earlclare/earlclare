// js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;

    if (path.includes('register.html')) {
        populateDistrictsDropdown();
        handleRegistrationForm();
    }

    if (path.includes('teams.html')) {
        displayTeamsByDistrict();
    }
});

// --- District Population for Registration Form ---
async function populateDistrictsDropdown() {
    const districtSelect = document.getElementById('district-select');
    if (!districtSelect) return;

    try {
        const response = await fetch('/api/districts'); // Assuming backend is on the same origin
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const districts = await response.json();
        
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district.id;
            option.textContent = district.name;
            districtSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load districts:', error);
        if (districtSelect) districtSelect.innerHTML = '<option value="">Error loading districts</option>';
    }
}

// --- Team Registration Form Handling ---
function handleRegistrationForm() {
    const registrationForm = document.getElementById('registrationForm'); // Assume form has id="registrationForm"
    const formMessagesDiv = document.getElementById('form-messages');

    if (!registrationForm || !formMessagesDiv) return;

    registrationForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        formMessagesDiv.textContent = ''; // Clear previous messages

        const formData = new FormData(registrationForm);
        const teamData = {
            team_name: formData.get('team_name'),
            company_name: formData.get('company_name'),
            district_id: parseInt(formData.get('district'), 10), // Ensure district_id is an integer
            // Assuming captain details are part of the form and have names like captain_name etc.
            // captain_name: formData.get('captain_name'),
            // captain_email: formData.get('captain_email'),
            // captain_phone: formData.get('captain_phone'),
            players: []
        };

        for (let i = 1; i <= 7; i++) {
            const playerName = formData.get(`player${i}_name`);
            if (playerName) { // Only add player if name is provided
                teamData.players.push({
                    name: playerName,
                    is_pro_player: formData.get(`player${i}_is_pro`) === 'on' // Checkbox value is 'on' if checked
                });
            }
        }
         
        // Basic client-side validation example (can be expanded)
        if (teamData.players.length === 0) {
            formMessagesDiv.textContent = 'Error: At least one player must be added.';
            formMessagesDiv.style.color = 'red';
            return;
        }

        try {
            const response = await fetch('/api/teams/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(teamData),
            });

            const result = await response.json();

            if (response.ok) {
                formMessagesDiv.textContent = result.message || 'Team registered successfully!';
                formMessagesDiv.style.color = 'green';
                registrationForm.reset(); // Clear form on success
            } else {
                formMessagesDiv.textContent = 'Error: ' + (result.error || 'Could not register team.');
                if(result.message) formMessagesDiv.textContent += ' Details: ' + result.message;
                formMessagesDiv.style.color = 'red';
            }
        } catch (error) {
            console.error('Registration submission error:', error);
            formMessagesDiv.textContent = 'An unexpected error occurred. Please try again.';
            formMessagesDiv.style.color = 'red';
        }
    });
}

// --- Display Teams on Teams Page ---
async function displayTeamsByDistrict() {
    const teamsContainer = document.getElementById('teams-by-district-container'); // Main container for all districts
    if (!teamsContainer) return;

    try {
        const response = await fetch('/api/teams');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const teams = await response.json();

        if (teams.length === 0) {
            teamsContainer.innerHTML = '<p>No teams registered yet.</p>';
            return;
        }

        // Group teams by district_name
        const teamsGroupedByDistrict = teams.reduce((acc, team) => {
            const districtName = team.district_name || 'Unknown District';
            if (!acc[districtName]) {
                acc[districtName] = [];
            }
            acc[districtName].push(team);
            return acc;
        }, {});
         
        teamsContainer.innerHTML = ''; // Clear any existing static content

        for (const districtName in teamsGroupedByDistrict) {
            const districtSection = document.createElement('div');
            districtSection.className = 'district-teams-section'; // For styling
            
            const districtHeader = document.createElement('h2');
            districtHeader.textContent = districtName;
            districtSection.appendChild(districtHeader);

            const teamsList = document.createElement('ul');
            teamsList.className = 'teams-list'; // For styling

            teamsGroupedByDistrict[districtName].forEach(team => {
                const teamItem = document.createElement('li');
                teamItem.className = 'team-item'; // For styling (e.g., card)
                
                let proPlayerCount = 0;
                const playersHtml = team.players.map(player => {
                    if(player.is_pro_player) proPlayerCount++;
                    return `<li>${player.name} ${player.is_pro_player ? '(Pro)' : ''}</li>`;
                }).join('');

                teamItem.innerHTML = `
                    <h3>${team.name}</h3>
                    <p><strong>Company:</strong> ${team.company_name || 'N/A'}</p>
                    <p><strong>Pro Players:</strong> ${proPlayerCount} / ${team.pro_player_count} (reported by API)</p>
                    <h4>Players:</h4>
                    <ul>${playersHtml}</ul>
                `;
                teamsList.appendChild(teamItem);
            });
            districtSection.appendChild(teamsList);
            teamsContainer.appendChild(districtSection);
        }

    } catch (error) {
        console.error('Failed to load teams:', error);
        teamsContainer.innerHTML = '<p>Error loading teams. Please try again later.</p>';
    }
}
