document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = '/api/v1';

    // DOM Elements
    const servicesGrid = document.getElementById('services-grid');
    const statActive = document.getElementById('stat-active');
    const statRules = document.getElementById('stat-rules');
    
    const btnRefresh = document.getElementById('btn-refresh');
    const btnCreateModal = document.getElementById('btn-create-modal');
    
    // Modal Elements
    const createModal = document.getElementById('create-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnCancel = document.getElementById('btn-cancel');
    const btnDeploy = document.getElementById('btn-deploy');
    const configInput = document.getElementById('config-input');
    const modalError = document.getElementById('modal-error');

    // Test Modal Elements
    const testModal = document.getElementById('test-modal');
    const testSvcName = document.getElementById('test-svc-name');
    const testCorrId = document.getElementById('test-corr-id');
    const testBodyInput = document.getElementById('test-body-input');
    const btnSendTest = document.getElementById('btn-send-test');
    const testModalError = document.getElementById('test-modal-error');
    let currentTestQueue = '';
    
    // Toast
    const toast = document.getElementById('toast');

    // --- Core Functions ---

    async function fetchServices() {
        try {
            const res = await fetch(`${API_BASE}/services`);
            if (!res.ok) throw new Error('Failed to fetch services');
            const data = await res.json();
            renderServices(data);
            updateStats(data);
        } catch (error) {
            showToast(error.message, true);
        }
    }

    function renderServices(services) {
        servicesGrid.innerHTML = '';
        
        // Update filter dropdown options
        const logFilter = document.getElementById('log-filter');
        const currentFilter = logFilter.value;
        logFilter.innerHTML = '<option value="all">All Services</option>';
        services.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.service_name;
            opt.textContent = s.service_name;
            logFilter.appendChild(opt);
        });
        logFilter.value = currentFilter;

        if (services.length === 0) {
            servicesGrid.innerHTML = '<p class="helper-text" style="grid-column: 1/-1; text-align: center;">No virtual services deployed yet.</p>';
            return;
        }

        services.forEach(svc => {
            const rulesCount = svc.rules ? svc.rules.length : 0;
            const statusClass = svc.active ? 'badge-active' : 'badge-inactive';
            const statusText = svc.active ? 'Active' : 'Inactive';

            const card = document.createElement('div');
            card.className = `service-card glass-panel ${svc.active ? '' : 'inactive'}`;
            card.innerHTML = `
                <div class="service-header">
                    <div>
                        <h3 class="service-title">${svc.service_name}</h3>
                        <span class="service-type">${svc.service_type.toUpperCase()}</span>
                    </div>
                    <span class="${statusClass}">${statusText}</span>
                </div>
                
                <div class="service-queues">
                    <div>
                        <div class="queue-label">Input Queue</div>
                        <div class="queue-name">${svc.input_queue}</div>
                    </div>
                    <div>
                        <div class="queue-label">Output Queue</div>
                        <div class="queue-name">${svc.output_queue}</div>
                    </div>
                </div>

            <div class="service-footer">
                    <div>
                        <span class="rules-count">${rulesCount} Matching Rules</span>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="primary-btn" onclick="openTestModal('${svc.service_name}', '${svc.input_queue}')" style="padding: 0.4rem 0.8rem; font-size: 0.75rem;">Test</button>
                        <button class="secondary-btn" onclick="deleteService('${svc.service_name}')" style="color: var(--danger); border-color: rgba(255,59,48,0.3); padding: 0.4rem 0.8rem; font-size: 0.75rem;">Delete</button>
                    </div>
                </div>
            `;
            servicesGrid.appendChild(card);
        });
    }

    function updateStats(services) {
        let activeCount = 0;
        let rulesCount = 0;
        
        services.forEach(svc => {
            if (svc.active) activeCount++;
            if (svc.rules) rulesCount += svc.rules.length;
        });

        statActive.textContent = activeCount;
        statRules.textContent = rulesCount;
    }

    async function deployService() {
        try {
            modalError.classList.add('hidden');
            const configText = configInput.value;
            const configJson = JSON.parse(configText);

            const res = await fetch(`${API_BASE}/services`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configJson)
            });

            if (!res.ok) {
                const errData = await res.json();
                let errMsg = 'Failed to deploy service';
                if (errData.detail && Array.isArray(errData.detail)) {
                    errMsg = errData.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n');
                } else if (errData.detail) {
                    errMsg = errData.detail;
                }
                throw new Error(errMsg);
            }

            showToast('Service deployed successfully!');
            closeModal();
            fetchServices();
        } catch (error) {
            modalError.textContent = `Error: ${error.message}`;
            modalError.classList.remove('hidden');
        }
    }

    window.deleteService = async function(name) {
        if (!confirm(`Are you sure you want to delete ${name}?`)) return;
        
        try {
            const res = await fetch(`${API_BASE}/services/${name}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to delete service');
            
            showToast('Service deleted.');
            fetchServices();
        } catch (error) {
            showToast(error.message, true);
        }
    }

    function showToast(msg, isError = false) {
        toast.textContent = msg;
        toast.className = `toast ${isError ? 'error' : ''}`;
        toast.classList.remove('hidden');
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    // --- Modal Handling ---
    function openModal() {
        createModal.classList.remove('hidden');
        modalError.classList.add('hidden');
    }

    function closeModal() {
        createModal.classList.add('hidden');
    }

    window.openTestModal = function(name, queue) {
        testSvcName.textContent = name;
        currentTestQueue = queue;
        testCorrId.value = `TEST-${Math.floor(Math.random()*1000)}`;
        testModal.classList.remove('hidden');
        testModalError.classList.add('hidden');
    }

    function closeTestModal() {
        testModal.classList.add('hidden');
    }

    async function sendTestMessage() {
        try {
            testModalError.classList.add('hidden');
            const body = testBodyInput.value;
            const corrId = testCorrId.value;

            const params = new URLSearchParams({
                queue_name: currentTestQueue,
                body: body,
                correlation_id: corrId
            });

            const res = await fetch(`${API_BASE}/test/inject?${params.toString()}`, {
                method: 'POST'
            });

            if (!res.ok) throw new Error('Failed to inject test message');

            showToast('Test message triggered!');
            closeTestModal();
        } catch (error) {
            testModalError.textContent = `Error: ${error.message}`;
            testModalError.classList.remove('hidden');
        }
    }

    async function aiGenerateConfig() {
        const promptInput = document.getElementById('ai-prompt');
        const btnAi = document.getElementById('btn-ai-generate');
        const prompt = promptInput.value;

        if (!prompt) return;

        try {
            btnAi.disabled = true;
            btnAi.textContent = 'Thinking...';
            
            const res = await fetch(`${API_BASE}/ai/generate-config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            if (!res.ok) throw new Error('AI generation failed');

            const config = await res.json();
            configInput.value = JSON.stringify(config, null, 2);
            showToast('AI generated a new configuration!');
        } catch (error) {
            showToast('AI Error: ' + error.message, 'error');
        } finally {
            btnAi.disabled = false;
            btnAi.textContent = 'Generate';
        }
    }

    // --- Event Listeners ---
    btnRefresh.addEventListener('click', fetchServices);
    btnCreateModal.addEventListener('click', openModal);
    btnCloseModal.addEventListener('click', closeModal);
    btnCancel.addEventListener('click', closeModal);
    btnDeploy.addEventListener('click', deployService);
    document.getElementById('btn-ai-generate').addEventListener('click', aiGenerateConfig);

    document.getElementById('btn-close-test-modal').addEventListener('click', closeTestModal);
    document.getElementById('btn-test-cancel').addEventListener('click', closeTestModal);
    btnSendTest.addEventListener('click', sendTestMessage);

    // Initial load
    fetchServices();
    fetchLogs();
    
    // Poll for logs every 2 seconds
    setInterval(fetchLogs, 2000);

    async function fetchLogs() {
        try {
            const res = await fetch(`${API_BASE}/logs`);
            if (!res.ok) return;
            const data = await res.json();
            renderLogs(data);
        } catch (e) {}
    }

    function renderLogs(logs) {
        const logsBody = document.getElementById('logs-body');
        const filterValue = document.getElementById('log-filter').value;
        if (!logsBody) return;
        
        let filteredLogs = logs;
        if (filterValue !== 'all') {
            filteredLogs = logs.filter(l => l.service === filterValue);
        }

        if (filteredLogs.length === 0) {
            logsBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-secondary);">No messages intercepted ${filterValue === 'all' ? 'yet' : 'for ' + filterValue}.</td></tr>`;
            return;
        }

        // Show last 10 logs, newest first
        const displayLogs = [...filteredLogs].reverse().slice(0, 10);
        
        logsBody.innerHTML = displayLogs.map(log => `
            <tr>
                <td class="log-time">${new Date(log.timestamp * 1000).toLocaleTimeString()}</td>
                <td class="log-service">${log.service}</td>
                <td><span class="log-rule">${log.rule}</span></td>
                <td class="log-latency">${log.latency_ms}ms</td>
                <td class="log-preview">${log.request_preview}</td>
                <td class="log-preview">${log.response_preview}</td>
            </tr>
        `).join('');
    }
});
