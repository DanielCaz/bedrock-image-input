import { useMutation } from "@tanstack/react-query";
import { presignedUrl } from "../api";

export const usePresignedUrl = () => {
  return useMutation({
    mutationFn: presignedUrl,
  });
};
