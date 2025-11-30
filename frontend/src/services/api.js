import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const predictFault = async (signal) => {
  const response = await axios.post(`${API_BASE_URL}/predict`, { signal });
  return response.data;
};

export const getExampleSignal = async (type) => {
  const response = await axios.get(`${API_BASE_URL}/example/${type}`);
  return response.data;
};

export const downloadDiagnosticReport = async (signal) => {
  const response = await axios.post(`${API_BASE_URL}/diagnostic-report`, 
    { signal },
    { responseType: 'blob' }
  );
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `diagnostic_report_${Date.now()}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};
