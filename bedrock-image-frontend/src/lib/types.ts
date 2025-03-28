type ApiBaseResponse<T> = T & {
  message: string;
};

export type ApiPresignedUrlResponse = ApiBaseResponse<{
  url: string;
  fields: Record<string, string>;
}>;
