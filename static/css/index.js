document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('dataBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const totalRowsIndicator = document.getElementById('totalRowsIndicator');
    
    // Track loading state
    let isLoading = false;
    let isCompleted = false;
    let totalRowsLoaded = 0;

    function loadMoreData() {
        // Prevent multiple simultaneous loads
        if (isLoading || isCompleted) return;

        isLoading = true;
        loadingIndicator.textContent = 'Loading more data...';
        loadingIndicator.style.display = 'block';

        fetch('/load_data')
            .then(response => {
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

                                // Add rows to the table
                                chunkData.rows.forEach((rowData, index) => {
                                    const tr = document.createElement('tr');
                                    // Add index column
                                    const indexTd = document.createElement('td');
                                    indexTd.textContent = totalRowsLoaded + index + 1;
                                    tr.appendChild(indexTd);

                                    Object.keys(rowData).forEach(key => {
                                        const td = document.createElement('td');
                                        td.textContent = rowData[key] !== null ? rowData[key] : '';
                                        tr.appendChild(td);
                                    });
                                    tbody.appendChild(tr);
                                });

                                totalRowsLoaded += chunkData.rows.length;

                                isLoading = false;
                                loadingIndicator.style.display = 'none';
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

    // Initial data load
    loadMoreData();

    // Add scroll-based loading
    window.addEventListener('scroll', () => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            loadMoreData();
        }
    });
});