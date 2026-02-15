/** Javascript */
 document.getElementById('file-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
                    const data = JSON.parse(e.target.result);
                    displayScores(data);
                } catch (error) {
                    alert("Erreur de lecture du fichier JSON. Assurez-vous qu'il est valide.");
                }
            };
            reader.readAsText(file);
        });

        function displayScores(data) {
            const tbody = document.getElementById('scoreBody');
            tbody.innerHTML = '';

            // Convertir l'objet JSON en tableau [clé, valeur] et trier
            let sortedScores = [];
            for (let user in data) {
                sortedScores.push([user, data[user]]);
            }
            sortedScores.sort((a, b) => b[1] - a[1]); // Tri décroissant

            // Afficher le top 10
            sortedScores.slice(0, 10).forEach((item, index) => {
                const row = `<tr>
                    <td>${index + 1}</td>
                    <td>${item[0]}</td>
                    <td><strong>${item[1]}</strong></td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }



        aaajhzehuyguyezrfgh
        tyyrt
        gdyujheruutrgutgfuuirtfg
        hyuyuuuujuj
            ytytytytytytytytytytytytytytytytytytytytytytytytytytytytyt