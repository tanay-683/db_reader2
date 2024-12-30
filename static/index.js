class DataStreamProcessor {
    constructor() {
        this.allData = [];
        this.pageSize = 20;
        this.currentPage = 1;
        this.columns = [];
        this.buffer = '';
        
        this.tableContainer = document.querySelector('.q_table');
        this.paginationContainer = document.querySelector('.pagination');
        this.tableBody = document.getElementById('tableBody');
        this.prevButton = document.getElementById('prevButton');
        this.nextButton = document.getElementById('nextButton');
        this.pageInfo = document.getElementById('pageInfo');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorMessage = document.getElementById('errorMessage');
        this.queryInput = document.getElementById('queryInput');
        this.queryButton = document.getElementById('queryButton');
        
        this.prevButton.addEventListener('click', () => this.changePage(-1));
        this.nextButton.addEventListener('click', () => this.changePage(1));
        this.queryButton.addEventListener('click', () => this.submitQuery());

        this.hideDataDisplay();  // Initial state
    }
    
    hideDataDisplay() {
        this.tableContainer.style.display = 'none';
        this.paginationContainer.style.display = 'none';
    }

    showDataDisplay() {
        this.tableContainer.style.display = 'block';
        this.paginationContainer.style.display = 'flex';
    }
    
    resetUI() {
        this.allData = [];
        this.columns = [];
        this.tableBody.innerHTML = '';
        const headerRow = document.querySelector('#dataTable thead tr');
        headerRow.innerHTML = '<th>Index</th>';
        
        this.loadingIndicator.style.display = 'block';
        this.errorMessage.textContent = '';
        this.hideDataDisplay();
    }
    
    submitQuery() {
        
        const query = this.queryInput.value.trim();
        
        if (!query) {
            this.errorMessage.textContent = 'Please enter a valid SQL query';
            return;
        }
        
        this.resetUI();
        this.startDataFetch(query);
    }
    
    startDataFetch(query) {
        fetch(`/load_data?query=${encodeURIComponent(query)}`)
            .then(response => response.body.getReader())
            .then(reader => {
                const decoder = new TextDecoder();
                const processChunk = ({ done, value }) => {
                    if (done) {
                        this.processRemainingBuffer();
                        this.onDataComplete();
                        return;
                    }
                    
                    const chunk = decoder.decode(value, { stream: true });
                    this.buffer += chunk;
                    this.processBuffer();
                    
                    reader.read().then(processChunk);
                };
                
                reader.read().then(processChunk);
            })
            .catch(error => {
                console.error('Fetch error:', error);
                this.loadingIndicator.style.display = 'none';
                this.errorMessage.textContent = `Error loading data: ${error.message}`;
            });
    }
    
    processBuffer() {
        const lines = this.buffer.split('\n');
        this.buffer = lines.pop() || '';
        
        lines.forEach(line => {
            if (line.trim()) {
                try {
                    const data = JSON.parse(line);
                    if (data.error) {
                        this.errorMessage.textContent = data.error;
                        this.loadingIndicator.style.display = 'none';
                        return;
                    }
                    
                    if (data.rows) {
                        if (data.columns && this.columns.length === 0) {
                            this.columns = data.columns;
                            const headerRow = document.querySelector('#dataTable thead tr');
                            this.columns.forEach(column => {
                                const th = document.createElement('th');
                                th.textContent = column;
                                headerRow.appendChild(th);
                            });
                            this.showDataDisplay();  // Show only when data arrives
                        }
                        
                        this.allData.push(...data.rows);
                        this.renderPage(this.currentPage);
                    }
                } catch (parseError) {
                    console.error('JSON parse error:', parseError);
                }
            }
        });
    }
    
    processRemainingBuffer() {
        if (this.buffer.trim()) {
            try {
                const data = JSON.parse(this.buffer);
                if (data.rows) {
                    this.allData.push(...data.rows);
                }
            } catch (error) {
                console.error('Final buffer parse error:', error);
            }
        }
    }
    
    onDataComplete() {
        this.loadingIndicator.style.display = 'none';
        this.renderPage(1);
        this.updatePaginationControls();
    }
    
    renderPage(pageNumber) {
        this.currentPage = pageNumber;
        const startIndex = (pageNumber - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.allData.slice(startIndex, endIndex);
        
        this.tableBody.innerHTML = '';
        
        pageData.forEach((row, index) => {
            const tr = document.createElement('tr');
            
            const indexCell = document.createElement('td');
            indexCell.textContent = startIndex + index + 1;
            tr.appendChild(indexCell);
            
            this.columns.forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column] ?? 'N/A';
                tr.appendChild(td);
            });
            
            this.tableBody.appendChild(tr);
        });
        
        this.updatePaginationControls();
    }
    
    updatePaginationControls() {
        const totalPages = Math.ceil(this.allData.length / this.pageSize);
        
        this.prevButton.disabled = this.currentPage <= 1;
        this.nextButton.disabled = this.currentPage >= totalPages;
        
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
    }
    
    changePage(delta) {
        const newPage = this.currentPage + delta;
        if (newPage >= 1 && newPage <= Math.ceil(this.allData.length / this.pageSize)) {
            this.renderPage(newPage);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DataStreamProcessor();
});
