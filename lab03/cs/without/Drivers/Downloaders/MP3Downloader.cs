using BookDownloader.Models;
using System.Text.RegularExpressions;

namespace BookDownloader.Drivers.Downloaders;

public class MP3Downloader : BaseAudioDownloader
{
    public MP3Downloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler) { }

    public override bool DownloadBook()
    {
        try
        {
            System.Diagnostics.Debug.WriteLine("preparing downloading");
            Prepare();
            if (!Terminated)
            {
                System.Diagnostics.Debug.WriteLine("downloading started");
                ProcessHandler.InitStatus(DownloadProcessStatus.Downloading, TotalSize);
                DownloadFiles();
            }
            if (!Terminated)
            {
                System.Diagnostics.Debug.WriteLine("finishing downloading");
                ProcessHandler.InitStatus(DownloadProcessStatus.Finishing);
                Finish();
            }

            if (Terminated)
            {
                ProcessHandler.InitStatus(DownloadProcessStatus.Terminated);
                System.Diagnostics.Debug.WriteLine("terminated");
            }
            else
            {
                ProcessHandler.InitStatus(DownloadProcessStatus.Finished);
                System.Diagnostics.Debug.WriteLine("finished");
            }

            return !Terminated;
        }
        finally
        {
            HttpClient?.Dispose();
        }
    }

    protected void Prepare()
    {
        Files = PrepareFilesData();
        ProcessHandler.InitStatus(DownloadProcessStatus.Preparing, Files.Count);
        CalcTotalSize();
    }

    protected void CalcTotalSize()
    {
        foreach (var file in Files)
        {
            if (Terminated) return;
            AddFileSize(file);
        }
    }

    protected void AddFileSize(FileData file)
    {
        if (Terminated) return;
        if (!file.Size.HasValue)
        {
            try
            {
                var request = new HttpRequestMessage(HttpMethod.Head, file.Url);
                if (file.Extra.ContainsKey("headers"))
                {
                    var headers = (Dictionary<string, string>)file.Extra["headers"];
                    foreach (var header in headers)
                    {
                        request.Headers.Add(header.Key, header.Value);
                    }
                }

                var response = HttpClient.SendAsync(request).Result;
                var contentLength = response.Content.Headers.ContentLength;
                if (!contentLength.HasValue)
                {
                    throw new Exception("No content-length found");
                }
                file.Size = (int)contentLength.Value;
            }
            catch (Exception)
            {
                System.Threading.Thread.Sleep(1000);
                AddFileSize(file);
                return;
            }
        }
        TotalSize += file.Size.Value;
        ProcessHandler.Progress(1);
    }

    protected void DownloadFiles()
    {
        var bookDirPath = Book.DirPath;
        if (!Directory.Exists(bookDirPath))
        {
            Directory.CreateDirectory(bookDirPath);
        }

        foreach (var file in Files)
        {
            if (Terminated) return;
            DownloadFile(file);
        }
    }

    protected void DownloadFile(FileData file)
    {
        var filePath = Path.Combine(Book.DirPath, file.Name);
        System.Diagnostics.Debug.WriteLine($"downloading file {file.Index} {filePath} {file.Url}");

        using (var fileStream = File.Create(filePath))
        {
            var downloadedSize = 0;
            while (!Terminated)
            {
                try
                {
                    var chunks = IterChunks(file, downloadedSize);
                    foreach (var chunk in chunks)
                    {
                        if (Terminated) return;
                        var chunkSize = chunk.Length;
                        ProcessHandler.Progress(chunkSize);
                        downloadedSize += chunkSize;
                        fileStream.Write(chunk, 0, chunkSize);
                        fileStream.Flush();
                    }
                    if (file.Size.HasValue && downloadedSize < file.Size.Value)
                    {
                        throw new Exception("downloaded size lower than file size");
                    }
                    break;
                }
                catch (Exception)
                {
                    System.Threading.Thread.Sleep(5000);
                    System.Diagnostics.Debug.WriteLine($"retrying download file {file.Index}");
                }
            }
        }
        DownloadedFiles[file.Index] = filePath;
        FileDownloaded(file, filePath);
    }

    protected IEnumerable<byte[]> IterChunks(FileData file, int offset = 0)
    {
        var request = new HttpRequestMessage(HttpMethod.Get, file.Url);
        var headers = new Dictionary<string, string>();

        if (file.Extra.ContainsKey("headers"))
        {
            var extraHeaders = (Dictionary<string, string>)file.Extra["headers"];
            foreach (var header in extraHeaders)
            {
                headers[header.Key] = header.Value;
            }
        }

        headers["Range"] = $"bytes={offset}-";
        request.Headers.Clear();
        foreach (var header in headers)
        {
            request.Headers.Add(header.Key, header.Value);
        }

        var response = HttpClient.SendAsync(request).Result;
        var buffer = new byte[64 * 1024];
        using (var stream = response.Content.ReadAsStreamAsync().Result)
        {
            int bytesRead;
            while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
            {
                yield return buffer[..bytesRead];
            }
        }
    }

    protected void Finish()
    {
        var files = FinalFiles(DownloadedFiles);
        if (Terminated) return;
    }

    protected Dictionary<string, string> FinalFiles(Dictionary<int, string> downloadedFiles)
    {
        var files = new Dictionary<string, string>();
        for (int i = 0; i < downloadedFiles.Count; i++)
        {
            if (Terminated) break;
            var filePath = downloadedFiles[i];
            FinalFile(i, filePath, files);
        }
        return files;
    }

    protected void FinalFile(int fileIndex, string filePath, Dictionary<string, string> files)
    {
        files[Path.GetFileName(filePath)] = "";
    }

    public void Terminate()
    {
        System.Diagnostics.Debug.WriteLine($"{this} terminating");
        ProcessHandler.InitStatus(DownloadProcessStatus.Terminating);
        Terminated = true;

        System.Diagnostics.Debug.WriteLine($"clearing tree {Book.DirPath}");
        if (Directory.Exists(Book.DirPath))
        {
            Directory.Delete(Book.DirPath, true);
        }
    }

    protected string GetChapterFileName(int chapterIndex, string extension = ".mp3")
    {
        var item = Source.Chapters[chapterIndex];
        var chapterTitle = Regex.Replace(item.Title, @"^(\d+) (.+)", "$2");
        if (chapterTitle.EndsWith(".wav"))
        {
            extension = "";
        }
        return $"{(chapterIndex + 1).ToString().PadLeft(2, '0')}. {chapterTitle}{extension}";
    }

    protected void FileDownloaded(FileData file, string filePath)
    {
        // Prepare file metadata
        System.Diagnostics.Debug.WriteLine($"preparing file metadata {filePath}");
        PrepareFileMetadata(filePath, file.Index, Book.Author, Book.Title, Book.SeriesName);
    }

    protected void PrepareFileMetadata(string filePath, int fileIndex, string author, string title, string seriesName)
    {
        // Metadata preparation logic
    }

    protected List<FileData> PrepareFilesData()
    {
        var files = new List<FileData>();
        for (int i = 0; i < Source.Chapters.Count; i++)
        {
            var chapter = Source.Chapters[i];
            files.Add(new FileData(i, GetChapterFileName(i), chapter.Url));
        }
        return files;
    }
}
