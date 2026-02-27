using System.IO.Compression;
using BookDownloader.Models;

namespace BookDownloader.Drivers.Downloaders;

public class ZipDownloader : BaseTextDownloader
{
    public ZipDownloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler) { }

    protected override void FileDownloaded(FileData file, string filePath)
    {
        base.FileDownloaded(file, filePath);

        // Extract ZIP file
        using (var zip = ZipFile.OpenRead(filePath))
        {
            if (zip.Entries.Count > 0)
            {
                var entry = zip.Entries[0];
                var extractPath = Path.Combine(Path.GetDirectoryName(filePath), entry.Name);
                entry.ExtractToFile(extractPath, true);
            }
        }

        // Remove original ZIP
        File.Delete(filePath);

        // Rename extracted file
        var extractedFileName = Directory.GetFiles(Path.GetDirectoryName(filePath))[0];
        var newFileName = Path.Combine(Path.GetDirectoryName(filePath),
            Path.GetFileNameWithoutExtension(filePath) + Path.GetExtension(extractedFileName));
        File.Move(extractedFileName, newFileName);

        DownloadedFiles[file.Index] = newFileName;
    }
}
