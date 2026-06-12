import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export const sendMessage = async (message, history) => {
  const res = await API.post("/api/chat/", { message, history });
  return res.data;
};

export const getAllSchemes = async () => {
  const res = await API.get("/api/schemes/");
  return res.data;
};

export const searchSchemes = async (query) => {
  const res = await API.post("/api/chat/search", { query });
  return res.data;
};