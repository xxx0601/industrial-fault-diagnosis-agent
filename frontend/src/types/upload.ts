export type UploadItem = {
  file_id: string;
  filename: string;
  file_type: string;
  upload_time: string;
};

export type UploadListResponse = {
  items: UploadItem[];
  total: number;
};
