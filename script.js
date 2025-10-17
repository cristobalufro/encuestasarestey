document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const searchInput = document.getElementById('search-input');
    const exportAllButton = document.getElementById('export-all');

    const surveyContainers = {
        original: document.getElementById('survey-container-original'),
        coded: document.getElementById('survey-container-coded'),
        codebook: document.getElementById('survey-container-codebook'),
        fc: document.getElementById('survey-container-fc')
    };

    let surveyData = {
        original: [],
        coded: [],
        codebook: {},
        fc: []
    };

    // --- Data Fetching ---
    const fetchData = (url, type) => {
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok for ${url}`);
                }
                return response.json();
            })
            .then(data => {
                surveyData[type] = data;
                // We will call display functions after all data is fetched
            })
            .catch(error => console.error(`Error loading data for ${type}:`, error));
    };

    // Use Promise.all to wait for all data to be fetched before displaying
    Promise.all([
        fetchData('kobo_data_export.json', 'original'),
        fetchData('kobo_data_export_coded.json', 'coded'),
        fetchData('libro_codigos.json', 'codebook'),
        fetchData('ENCUESTAS1-60FC.json', 'fc')
    ]).then(() => {
        // Initial display
        displaySurveys('original', surveyData.original);
        displaySurveys('coded', surveyData.coded);
        displayCodebook(surveyData.codebook);
        displaySurveys('fc', surveyData.fc);
    });

    // --- Tab Functionality ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.getAttribute('data-tab');
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(target).classList.add('active');
            
            // Clear search input when switching tabs
            searchInput.value = '';
            // Refresh the display for the active tab to reset any search filters
            const activeData = surveyData[target];
            if (target === 'codebook') {
                displayCodebook(activeData);
            } else {
                displaySurveys(target, activeData);
            }
        });
    });

    // --- Display Functions ---
    function displaySurveys(type, surveys) {
        const container = surveyContainers[type];
        if (!container) return;
        container.innerHTML = '';
        if (!Array.isArray(surveys)) {
            console.error(`Data for ${type} is not an array.`);
            return;
        }
        surveys.forEach(survey => {
            const card = document.createElement('div');
            card.className = 'survey-card';
            let participantCode = survey['Código de participante'] || survey['PARTICIPANTE'] || survey['Paciente'] || 'N/A';
            let cardContent = `<h2>Código: ${participantCode}</h2>`;
            for (const key in survey) {
                if (key !== 'Código de participante' && key !== 'PARTICIPANTE' && key !== 'Paciente') {
                    cardContent += `<p><strong>${key}:</strong> ${survey[key] !== null ? survey[key] : 'N/A'}</p>`;
                }
            }
            card.innerHTML = cardContent;
            container.appendChild(card);
        });
    }

    function displayCodebook(codebook) {
        const container = surveyContainers.codebook;
        container.innerHTML = '';
        for (const variable in codebook) {
            const details = codebook[variable];
            const card = document.createElement('div');
            card.className = 'survey-card';
            let cardContent = `<h2>${variable}</h2>`;
            cardContent += `<p><strong>Pregunta:</strong> ${details.label}</p>`;
            
            if (details.categories) {
                cardContent += '<ul>';
                for (const code in details.categories) {
                    cardContent += `<li><strong>${code}:</strong> ${details.categories[code]}</li>`;
                }
                cardContent += '</ul>';
            }
            if (details.combinations) {
                cardContent += '<h4>Combinaciones:</h4><ul>';
                for (const code in details.combinations) {
                    cardContent += `<li><strong>${code}:</strong> ${details.combinations[code]}</li>`;
                }
                cardContent += '</ul>';
            }
            card.innerHTML = cardContent;
            container.appendChild(card);
        }
    }

    // --- Search Functionality ---
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const activeTab = document.querySelector('.tab-button.active').getAttribute('data-tab');
        
        if (activeTab === 'codebook') {
            // Search logic for codebook
            const filteredCodebook = {};
            for (const variable in surveyData.codebook) {
                const details = surveyData.codebook[variable];
                const searchableStrings = [
                    variable,
                    details.label,
                    ...Object.values(details.categories || {}),
                    ...Object.values(details.combinations || {})
                ];
                if (searchableStrings.some(s => String(s).toLowerCase().includes(searchTerm))) {
                    filteredCodebook[variable] = details;
                }
            }
            displayCodebook(filteredCodebook);
        } else {
            // Search logic for survey data
            const filteredSurveys = surveyData[activeTab].filter(survey => {
                return Object.values(survey).some(value =>
                    String(value).toLowerCase().includes(searchTerm)
                );
            });
            displaySurveys(activeTab, filteredSurveys);
        }
    });

    // --- Excel Export ---
    exportAllButton.addEventListener('click', () => {
        const workbook = XLSX.utils.book_new();

        // Sheet 1: Original Data
        if (surveyData.original.length > 0) {
            const wsOriginal = XLSX.utils.json_to_sheet(surveyData.original);
            XLSX.utils.book_append_sheet(workbook, wsOriginal, 'Encuestas Originales');
        }

        // Sheet 2: Coded Data
        if (surveyData.coded.length > 0) {
            const wsCoded = XLSX.utils.json_to_sheet(surveyData.coded);
            XLSX.utils.book_append_sheet(workbook, wsCoded, 'Encuestas Codificadas');
        }

        // Sheet 3: Codebook
        const codebookRecords = [];
        for (const variable in surveyData.codebook) {
            const details = surveyData.codebook[variable];
            const options = { ...details.categories, ...details.combinations };
            for (const code in options) {
                codebookRecords.push({
                    'Variable': variable,
                    'Pregunta': details.label,
                    'Código': code,
                    'Respuesta': options[code]
                });
            }
        }
        if (codebookRecords.length > 0) {
            const wsCodebook = XLSX.utils.json_to_sheet(codebookRecords);
            XLSX.utils.book_append_sheet(workbook, wsCodebook, 'Libro de Códigos');
        }

        // Sheet 4: FC Data
        if (surveyData.fc.length > 0) {
            const wsFc = XLSX.utils.json_to_sheet(surveyData.fc);
            XLSX.utils.book_append_sheet(workbook, wsFc, 'Encuestas FC');
        }

        // Save the workbook
        XLSX.writeFile(workbook, 'Reporte_Completo_Encuestas.xlsx');
    });
});