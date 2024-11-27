document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('dataBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const totalRowsIndicator = document.getElementById('totalRowsIndicator');
    const nextButton = document.getElementById('next-button');
    const prevButton = document.getElementById('prev-button');
    
    // Track loading state
    let isLoading = false;
    let isCompleted = false;
    let totalRowsLoaded = 0;
    let dataArray = [];
    let currentPage = 1;
    let rowsPerPage = 20;

    function loadMoreData() {
        // Prevent multiple simultaneous loads
        if (isLoading || isCompleted) return;

        isLoading = true;
        loadingIndicator.textContent = 'Loading more data...';
        loadingIndicator.style.display = 'block';

        fetch('/load_data')
            .then(response => {

                let hasStarted = false;
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                function processStream({ done, value }) {
                    if (done) {
                        isLoading = false;
                        isCompleted = true;
                        loadingIndicator.style.display = 'none';
                        return;
                    }

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    lines.forEach(line => {
                        if (line) {
                            try {
                                const chunkData = JSON.parse(line);

                                // Check for error
                                if (chunkData.error) {
                                    throw new Error(chunkData.error);
                                }

                                // Update total rows
                                if (chunkData.total_processed) {
                                    totalRowsIndicator.textContent = `Rows Loaded: ${chunkData.total_processed}`;
                                }

                                // Add rows to the data array
                                dataArray.push(...chunkData.rows);

                                isLoading = false;
                                loadingIndicator.style.display = 'none';

                                if (!hasStarted) {
                                    hasStarted = true;
                                    renderTable();
                                }
                            } catch (error) {
                                console.error('Error parsing chunk:', error);
                                errorMessage.textContent = `Error: ${error.message}`;
                                errorMessage.style.display = 'block';
                                isLoading = false;
                                loadingIndicator.style.display = 'none';
                            }
                        }
                    });

                    // Continue reading the stream
                    reader.read().then(processStream);
                }

                // Start reading the stream
                reader.read().then(processStream);
            })
            .catch(error => {
                console.error('Fetch error:', error);
                errorMessage.textContent = `Error loading data: ${error.message}`;
                errorMessage.style.display = 'block';
                isLoading = false;
                loadingIndicator.style.display = 'none';
            });
    }

    function renderTable() {
        tbody.innerHTML = '';
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        const currentPageData = dataArray.slice(startIndex, endIndex);
        currentPageData.forEach((rowData, index) => {
            const tr = document.createElement('tr');
            // Add index column
            const indexTd = document.createElement('td');
            indexTd.textContent = startIndex + index + 1;
            tr.appendChild(indexTd);

            Object.keys(rowData).forEach(key => {
                const td = document.createElement('td');
                td.textContent = rowData[key] !== null ? rowData[key] : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }

    // Initial data load
    loadMoreData();

    // Add event listeners for next and previous buttons
    nextButton.addEventListener('click', () => {
        if (currentPage < Math.ceil(dataArray.length / rowsPerPage)) {
            currentPage++;
            renderTable();
        }
    });

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    });

    // Render table initially
});