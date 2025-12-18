const { useState, useEffect } = React;

const ExperimentList = ({ experiments, onSelect, onCreate }) => (
    <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">Experiments</h2>
            <button onClick={onCreate} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm font-medium">
                + New Experiment
            </button>
        </div>
        <ul className="divide-y divide-gray-200">
            {experiments.map(exp => (
                <li key={exp.id} className="py-4 flex justify-between hover:bg-gray-50 cursor-pointer px-2 rounded transition" onClick={() => onSelect(exp.id)}>
                    <div>
                        <p className="text-sm font-medium text-gray-900">{exp.name}</p>
                        <p className="text-xs text-gray-500">ID: {exp.id}</p>
                    </div>
                    <div className="text-right">
                        <span className="text-xs text-gray-400">View Details &rarr;</span>
                    </div>
                </li>
            ))}
        </ul>
    </div>
);

const RunList = ({ experimentId, runs, onTriggerRun }) => (
    <div className="bg-white shadow rounded-lg p-6 mt-6">
        <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Runs for Experiment</h3>
            <div className="space-x-2">
                <a href={`/api/v1/reports/${experimentId}`} target="_blank" className="text-blue-600 hover:text-blue-800 text-sm font-medium underline">
                    View Report
                </a>
                <button onClick={onTriggerRun} className="bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 text-sm font-medium">
                    Run Now
                </button>
            </div>
        </div>
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
                <thead>
                    <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">F1</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Latency (p95)</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Run ID</th>
                    </tr>
                </thead>
                <tbody>
                    {runs.map(run => (
                        <tr key={run.id}>
                            <td className="px-4 py-2 whitespace-nowrap">
                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                    ${run.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 
                                      run.status === 'FAILED' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                    {run.status}
                                </span>
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-500">{run.metrics?.f1 ? run.metrics.f1.toFixed(4) : '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-500">{run.metrics?.p95_latency ? run.metrics.p95_latency.toFixed(4) : '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-400 font-mono">{run.id.substring(0,8)}...</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

const CreateExperimentModal = ({ isOpen, onClose, onSubmit }) => {
    if (!isOpen) return null;
    const [name, setName] = useState("");
    const [datasetId, setDatasetId] = useState("");
    const [connectionId, setConnectionId] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        // Hardcoded config for MVP demo
        const config = {
            name,
            dataset_id: datasetId,
            connection_id: connectionId,
            optimizer_config: { indexing_threshold: 20000 },
            vector_config: { size: 1536, distance: "Cosine" }
        };
        onSubmit(config);
    };

    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
            <div className="bg-white p-8 rounded-lg shadow-xl w-96">
                <h3 className="text-lg font-bold mb-4">Create Experiment</h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Name</label>
                        <input type="text" required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" 
                            value={name} onChange={e => setName(e.target.value)} />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Dataset ID (UUID)</label>
                        <input type="text" required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" 
                            value={datasetId} onChange={e => setDatasetId(e.target.value)} />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Connection ID (UUID)</label>
                        <input type="text" required className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" 
                            value={connectionId} onChange={e => setConnectionId(e.target.value)} />
                    </div>
                    <div className="flex justify-end space-x-3 mt-6">
                        <button type="button" onClick={onClose} className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300 text-sm">Cancel</button>
                        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">Create</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const App = () => {
    const [experiments, setExperiments] = useState([]);
    const [selectedExpId, setSelectedExpId] = useState(null);
    const [runs, setRuns] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchExperiments = async () => {
        const res = await fetch('/api/v1/experiments');
        if (res.ok) setExperiments(await res.json());
    };

    const fetchRuns = async (expId) => {
        const res = await fetch(`/api/v1/runs?experiment_id=${expId}`);
        if (res.ok) setRuns(await res.json());
    };

    useEffect(() => {
        fetchExperiments();
    }, []);

    useEffect(() => {
        if (selectedExpId) {
            fetchRuns(selectedExpId);
            const interval = setInterval(() => fetchRuns(selectedExpId), 5000); // Poll every 5s
            return () => clearInterval(interval);
        }
    }, [selectedExpId]);

    const handleCreateExperiment = async (config) => {
        const res = await fetch('/api/v1/experiments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        if (res.ok) {
            setIsModalOpen(false);
            fetchExperiments();
        } else {
            alert("Failed to create experiment");
        }
    };

    const handleTriggerRun = async () => {
        if (!selectedExpId) return;
        const res = await fetch(`/api/v1/experiments/${selectedExpId}/runs`, { method: 'POST' });
        if (res.ok) fetchRuns(selectedExpId);
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                    <img src="https://qdrant.tech/images/logo_with_text.svg" alt="Qdrant" className="h-8" onError={(e) => e.target.style.display='none'} />
                    Bench Dashboard
                </h1>
            </header>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1">
                    <ExperimentList 
                        experiments={experiments} 
                        onSelect={setSelectedExpId} 
                        onCreate={() => setIsModalOpen(true)} 
                    />
                </div>
                <div className="lg:col-span-2">
                    {selectedExpId ? (
                        <RunList 
                            experimentId={selectedExpId} 
                            runs={runs} 
                            onTriggerRun={handleTriggerRun} 
                        />
                    ) : (
                        <div className="bg-white shadow rounded-lg p-12 text-center text-gray-500">
                            Select an experiment to view details
                        </div>
                    )}
                </div>
            </div>

            <CreateExperimentModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)} 
                onSubmit={handleCreateExperiment} 
            />
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);




