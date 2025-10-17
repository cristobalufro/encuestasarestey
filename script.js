document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const searchInput = document.getElementById('search-input');

    const surveyContainers = {
        socioeconomicas: document.getElementById('survey-container-socioeconomicas'),
        fc: document.getElementById('survey-container-fc')
    };

    const exportButtons = {
        socioeconomicas: document.getElementById('export-socioeconomicas'),
        fc: document.getElementById('export-fc')
    };

    let surveyData = {
        socioeconomicas: [],
        fc: []
    };

    // Fetch Socioeconomic Data
    fetch('kobo_data_export.json')
        .then(response => response.json())
        .then(data => {
            surveyData.socioeconomicas = data;
            displaySurveys('socioeconomicas', data);
        })
        .catch(error => console.error('Error al cargar los datos de la encuesta socioeconómica:', error));

    // Fetch FC Data
    fetch('ENCUESTAS1-60FC.json')
        .then(response => response.json())
        .then(data => {
            surveyData.fc = data;
            displaySurveys('fc', data);
        })
        .catch(error => console.error('Error al cargar los datos de la encuesta FC:', error));

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.getAttribute('data-tab');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(target).classList.add('active');
        });
    });

    function displaySurveys(type, surveys) {
        const container = surveyContainers[type];
        container.innerHTML = '';
        surveys.forEach(survey => {
            const card = document.createElement('div');
            card.className = 'survey-card';

            let participantCode = survey['Código de participante'] || survey['PARTICIPANTE'] || survey['Paciente'];
            let cardContent = `<h2>Código de participante: ${participantCode}</h2>`;
            for (const key in survey) {
                if (key !== 'Código de participante' && key !== 'PARTICIPANTE' && key !== 'Paciente') {
                    cardContent += `<p><strong>${key}:</strong> ${survey[key] || 'N/A'}</p>`;
                }
            }
            card.innerHTML = cardContent;
            container.appendChild(card);
        });
    }

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const activeTab = document.querySelector('.tab-button.active').getAttribute('data-tab');
        
        const filteredSurveys = surveyData[activeTab].filter(survey => {
            return Object.values(survey).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            );
        });
        displaySurveys(activeTab, filteredSurveys);
    });

    exportButtons.socioeconomicas.addEventListener('click', () => {
        if (surveyData.socioeconomicas.length === 0) {
            alert('No hay datos para exportar.');
            return;
        }
        const desiredOrder = [
            "Código de participante", "Encuestador", "Zona", "Fecha", "Teléfono de contacto", "Dirección de domicilio", "Edad", "Nivel de empleo", "Ultimo nivel educacional alcanzado", "¿Tiene hijos?", "Numero de hijos/as", "Edades de los hijos", "¿Cuántas personas viven en el hogar?", "¿Cual es el ingreso familiar mensual aproximado? (contar a todos quienes aportan)", "¿Quienes aportan al ingreso familiar?", "Porfavor, especifique quien aporta ingresos a la familia", "¿Ha sido diagnosticada (en un servicio de salud) con algunas de estas enfermedades?", "Porfavor, especifique la enfermedad", "¿Esta recibiendo tratamiento para esta enfermedad que especificó?", "¿Está recibiendo tratamiento actualmente para alguna de estas enfermedades?", "¿Cómo calificaría su estado de salud general actual?", "¿Como calificaría su alimentación?", "¿Ha sido diagnosticada con algunas de estas enfermedades, en el ultimo año?", "¿Cual es su previsión de salud?", "Especifique que previsión de salud", "¿Actualmente usted fuma cigarrillos?", "¿Bebe alcohol?", "¿Con qué frecuencia Ud. consume alguna bebida alcohólica?", "¿Cuantos tragos de alcohol suele tomar en un día de consumo normal?", "¿Durante el último mes. sin contar su trabajo regular, participó en alguna actividad física como correr, jardinería, nadar, bailar o caminar?", "Porfavor, especifique su actividad", "Durante los últimos 7 días, ¿Cuánto tiempo permaneció sentado(a) al día durante la semana?", "Durante los últimos 7 días, ¿En cuántos caminó por lo menos 10 minutos seguidos?", "Habitualmente, ¿Cuántos minutos en total dedicó a caminar en uno de esos días?", "¿Usted realiza al menos 150 minutos (2,5 hrs.) de actividad física de intensidad Vigorosa o intensa a la semana *? *Actividades vigorosas o intensas: son aquellas que requieren un esfuerzo físico fuerte y le hacen respirar mucho más fuerte que lo normal. Ej. pedalear en bicicleta rápido o a velocidad normal.", "Peso (Kg)", "Estatura (centimetros)", "IMC", "Circunferencia de cintura", "% de grasa", "Grasa visceral", "% de musculo"
        ];
        const reorderedData = surveyData.socioeconomicas.map(survey => {
            const newSurvey = {};
            desiredOrder.forEach(key => {
                newSurvey[key] = survey[key];
            });
            return newSurvey;
        });
        const worksheet = XLSX.utils.json_to_sheet(reorderedData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Encuestas Socioeconómicas');
        XLSX.writeFile(workbook, 'encuestas_socioeconomicas.xlsx');
    });

    exportButtons.fc.addEventListener('click', () => {
        if (surveyData.fc.length === 0) {
            alert('No hay datos para exportar.');
            return;
        }
        const worksheet = XLSX.utils.json_to_sheet(surveyData.fc);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Encuestas FC');
        XLSX.writeFile(workbook, 'encuestas_fc.xlsx');
    });
});