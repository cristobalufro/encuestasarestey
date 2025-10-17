document.addEventListener('DOMContentLoaded', () => {
    const surveyContainer = document.getElementById('survey-container');
    const exportButton = document.getElementById('export-to-excel');
    const searchInput = document.getElementById('search-input');
    let surveyData = [];

    fetch('kobo_data_export.json')
        .then(response => response.json())
        .then(data => {
            surveyData = data;
            displaySurveys(data);
        })
        .catch(error => console.error('Error al cargar los datos de la encuesta:', error));

    function displaySurveys(surveys) {
        surveyContainer.innerHTML = '';
        surveys.forEach(survey => {
            const card = document.createElement('div');
            card.className = 'survey-card';

            let cardContent = `<h2>Código de participante: ${survey['Código de participante']}</h2>`;
            for (const key in survey) {
                if (key !== 'Código de participante') {
                    cardContent += `<p><strong>${key}:</strong> ${survey[key] || 'N/A'}</p>`;
                }
            }
            card.innerHTML = cardContent;
            surveyContainer.appendChild(card);
        });
    }

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredSurveys = surveyData.filter(survey => {
            return Object.values(survey).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            );
        });
        displaySurveys(filteredSurveys);
    });

    exportButton.addEventListener('click', () => {
        if (surveyData.length === 0) {
            alert('No hay datos para exportar.');
            return;
        }

        const desiredOrder = [
            "Código de participante",
            "Encuestador",
            "Zona",
            "Fecha",
            "Teléfono de contacto",
            "Dirección de domicilio",
            "Edad",
            "Nivel de empleo",
            "Ultimo nivel educacional alcanzado",
            "¿Tiene hijos?",
            "Numero de hijos/as",
            "Edades de los hijos",
            "¿Cuántas personas viven en el hogar?",
            "¿Cual es el ingreso familiar mensual aproximado? (contar a todos quienes aportan)",
            "¿Quienes aportan al ingreso familiar?",
            "Porfavor, especifique quien aporta ingresos a la familia",
            "¿Ha sido diagnosticada (en un servicio de salud) con algunas de estas enfermedades?",
            "Porfavor, especifique la enfermedad",
            "¿Esta recibiendo tratamiento para esta enfermedad que especificó?",
            "¿Está recibiendo tratamiento actualmente para alguna de estas enfermedades?",
            "¿Cómo calificaría su estado de salud general actual?",
            "¿Como calificaría su alimentación?",
            "¿Ha sido diagnosticada con algunas de estas enfermedades, en el ultimo año?",
            "¿Cual es su previsión de salud?",
            "Especifique que previsión de salud",
            "¿Actualmente usted fuma cigarrillos?",
            "¿Bebe alcohol?",
            "¿Con qué frecuencia Ud. consume alguna bebida alcohólica?",
            "¿Cuantos tragos de alcohol suele tomar en un día de consumo normal?",
            "¿Durante el último mes. sin contar su trabajo regular, participó en alguna actividad física como correr, jardinería, nadar, bailar o caminar?",
            "Porfavor, especifique su actividad",
            "Durante los últimos 7 días, ¿Cuánto tiempo permaneció sentado(a) al día durante la semana?",
            "Durante los últimos 7 días, ¿En cuántos caminó por lo menos 10 minutos seguidos?",
            "Habitualmente, ¿Cuántos minutos en total dedicó a caminar en uno de esos días?",
            "¿Usted realiza al menos 150 minutos (2,5 hrs.) de actividad física de intensidad Vigorosa o intensa a la semana *? *Actividades vigorosas o intensas: son aquellas que requieren un esfuerzo físico fuerte y le hacen respirar mucho más fuerte que lo normal. Ej. pedalear en bicicleta rápido o a velocidad normal.",
            "Peso (Kg)",
            "Estatura (centimetros)",
            "IMC",
            "Circunferencia de cintura",
            "% de grasa",
            "Grasa visceral",
            "% de musculo"
        ];

        const reorderedData = surveyData.map(survey => {
            const newSurvey = {};
            desiredOrder.forEach(key => {
                newSurvey[key] = survey[key];
            });
            return newSurvey;
        });

        const worksheet = XLSX.utils.json_to_sheet(reorderedData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Surveys');
        XLSX.writeFile(workbook, 'kobo_data_export.xlsx');
    });
});