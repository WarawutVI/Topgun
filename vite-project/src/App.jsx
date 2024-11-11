import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const accessToken ='fjwfji3399';
const apiUrl = 'http://localhost:8000/api/v1/users';

// Set up the interceptor
axios.interceptors.request.use(
    config => {
        config.headers.authorization = `Bearer ${accessToken}`;
        return config;
    },
    error => {
        return Promise.reject(error);
    });

function App() {
    const [data, setData] = useState([]);
    const [requestError, setRequestError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await axios.get(apiUrl);
                setUsers(result.data);
            } catch (error) {
                setRequestError(error.message);
            }
        };
        fetchData();
    }, []);

    return (
        <div>
            {requestError ? (
                <p>Error: {requestError}</p>
            ) : (
                <ul>
                    {data.map(data => (
                        <li key={data.id}>{data.name}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}



export default App;
