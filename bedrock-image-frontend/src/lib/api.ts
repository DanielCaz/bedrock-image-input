import { ApiPresignedUrlResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL;

export const presignedUrl = async (file: File) => {
  const res = await fetch(`${API_URL}/presigned`, {
    method: "POST",
  });

  const data: ApiPresignedUrlResponse = await res.json();

  if (!res.ok) {
    throw new Error(data.message);
  }

  const { url, fields } = data;

  const formData = new FormData();

  Object.entries(fields).forEach(([key, value]) => {
    formData.append(key, value);
  });

  formData.append("file", file);

  const uploadRes = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!uploadRes.ok) {
    throw new Error("Failed to upload file");
  }
};
