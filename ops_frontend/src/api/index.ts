import axios from 'axios';

export const fetchData = () => {
    return axios.get( './table.json');
};
