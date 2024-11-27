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
        
        this.prevButton.addEventListener('click', () => this.changePage(-1));
        this.nextButton.addEventListener('click', () => this.changePage(1));
        
        this.startDataFetch();
    }
    
    startDataFetch() {
        fetch('/load_data')
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
            // Split by newline and process complete JSON objects
            const lines = this.buffer.split('\n');
            
            // Keep the last (potentially incomplete) line in the buffer
            this.buffer = lines.pop() || '';
            
            lines.forEach(line => {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        if (data.rows) {
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
        
        // Log total rows for debugging
        console.log(`Total rows received: ${this.allData.length}`);
        
        this.renderPage(1);
        this.updatePaginationControls();
    }
    
    renderPage(pageNumber) {
        this.currentPage = pageNumber;
        const startIndex = (pageNumber - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.allData.slice(startIndex, endIndex);
        
        this.tableBody.innerHTML = ''; // Clear previous rows
        
        // Dynamically generate headers if not already done
        if (this.columns.length === 0 && this.allData.length > 0) {
            this.columns = Object.keys(this.allData[0]);
            const headerRow = document.querySelector('#dataTable thead tr');
            this.columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column;
                headerRow.appendChild(th);
            });
        }
        
        // Render rows
        pageData.forEach((row, index) => {
            const tr = document.createElement('tr');
            
            // Add index column
            const indexCell = document.createElement('td');
            indexCell.textContent = startIndex + index + 1;
            tr.appendChild(indexCell);
            
            // Add data columns
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
        
        // Log pagination details for debugging
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

// Initialize the data stream processor when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new DataStreamProcessor();
});