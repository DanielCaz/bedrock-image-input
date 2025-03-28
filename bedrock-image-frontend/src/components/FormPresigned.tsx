import { usePresignedUrl } from "../lib/mutations/usePresignedUrl";

const FormPresigned = () => {
  const { mutate, isPending } = usePresignedUrl();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);

    const file = formData.get("file") as File;

    mutate(file);
  };

  return (
    <form onSubmit={handleSubmit}>
      <fieldset className="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
        <legend className="fieldset-legend">Pre-Signed URLs</legend>

        <label className="fieldset-label">File</label>
        <input
          required
          type="file"
          name="file"
          className="file-input"
          accept=".pdf"
        />

        <button
          type="submit"
          className="btn btn-neutral mt-4"
          disabled={isPending}
        >
          {isPending ? (
            <span className="loading loading-spinner loading-sm"></span>
          ) : null}
          Upload
        </button>
      </fieldset>
    </form>
  );
};

export default FormPresigned;
