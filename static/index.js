class DataStreamProcessor {
    constructor() {
        this.allData = [];
        this.pageSize = 20;
        this.currentPage = 1;
        this.columns = [];
        this.buffer = '';
        
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
    }
    
    resetUI() {
        this.allData = [];
        this.columns = [];
        this.tableBody.innerHTML = '';
        const headerRow = document.querySelector('#dataTable thead tr');
        headerRow.innerHTML = '<th>Index</th>'; // Reset headers
        
        this.loadingIndicator.style.display = 'block';
        this.errorMessage.textContent = '';
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
            .then(response => {
                const reader = response.body.getReader();
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
        try {
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
                            if (data.columns) {
                                this.columns = data.columns;
                                const headerRow = document.querySelector('#dataTable thead tr');
                                this.columns.forEach(column => {
                                    const th = document.createElement('th');
                                    th.textContent = column;
                                    headerRow.appendChild(th);
                                });
                            }
                            
                            this.allData.push(...data.rows);
                            this.renderPage(this.currentPage);
                        }
                    } catch (parseError) {
                        console.error('JSON parse error:', parseError);
                    }
                }
            });
        } catch (error) {
            console.error('Buffer processing error:', error);
        }
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
        console.log(`Total rows received: ${this.allData.length}`);
        
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
        console.log(`Total rows: ${this.allData.length}, Page size: ${this.pageSize}, Total pages: ${totalPages}`);
    }
    
    changePage(delta) {
        const totalPages = Math.ceil(this.allData.length / this.pageSize);
        const newPage = this.currentPage + delta;
        
        if (newPage >= 1 && newPage <= totalPages) {
            this.renderPage(newPage);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DataStreamProcessor();
});