using BookDownloader.Models;

namespace BookDownloader.Drivers.Downloaders;

public class M3U8Downloader : BaseAudioDownloader
{
    private List<System.Threading.Tasks.Task> fixesTasks;

    public M3U8Downloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler)
    {
        fixesTasks = new List<System.Threading.Tasks.Task>();
    }

    protected override List<FileData> PrepareFilesData()
    {
        // Этот метод не используется в M3U8Downloader, так как подготовка происходит по-другому
        return new List<FileData>();
    }

    protected override void Prepare()
    {
        ProcessHandler.InitStatus(DownloadProcessStatus.Preparing, Source.Chapters.Count);
        TotalSize = 0;

        for (int i = 0; i < Source.Chapters.Count; i++)
        {
            var chapter = Source.Chapters[i];
            PrepareFileData(i, chapter);
        }

        Files.Sort((x, y) => x.Index.CompareTo(y.Index));
    }

    private void PrepareFileData(int chapterIndex, Chapter chapter)
    {
        // M3U8 file parsing
    }

    protected override void FileDownloaded(FileData file, string filePath)
    {
        // Добавляем задачу исправления метаданных M4A
        var task = System.Threading.Tasks.Task.Run(() => FixM4AMeta(filePath));
        fixesTasks.Add(task);
        base.FileDownloaded(file, filePath);
    }

    protected override void Finish()
    {
        System.Threading.Tasks.Task.WaitAll(fixesTasks.ToArray());
        base.Finish();
    }

    protected override IEnumerable<byte[]> IterChunks(FileData file, int offset = 0)
    {
        var currentRangeIndex = file.Extra.ContainsKey("current_range_index") ?
            (int)file.Extra["current_range_index"] : 0;

        if (file.Extra.ContainsKey("ranges"))
        {
            var ranges = (List<object>)file.Extra["ranges"];
            if (currentRangeIndex < ranges.Count)
            {
                var rangeObj = ranges[currentRangeIndex];
                var byterangeProp = rangeObj.GetType().GetProperty("Byterange");
                if (byterangeProp != null)
                {
                    var byterange = (string)byterangeProp.GetValue(rangeObj);
                    if (!string.IsNullOrEmpty(byterange))
                    {
                        var parts = byterange.Split('@');
                        if (parts.Length == 2)
                        {
                            var length = long.Parse(parts[0]);
                            var start = long.Parse(parts[1]);

                            var headers = new Dictionary<string, string>
                            {
                                ["Range"] = $"bytes={Math.Max(offset, start)}-{start + length - 1}"
                            };
                            file.Extra["headers"] = headers;
                        }
                    }
                }

                foreach (var chunk in base.IterChunks(file, 0))
                {
                    yield return chunk;
                }
            }

            if (currentRangeIndex + 1 < ranges.Count)
            {
                file.Extra["current_range_index"] = currentRangeIndex + 1;
                foreach (var chunk in IterChunks(file, offset))
                {
                    yield return chunk;
                }
            }
        }
        else
        {
            foreach (var chunk in base.IterChunks(file, offset))
            {
                yield return chunk;
            }
        }
    }

    protected override void _Terminate()
    {
        if (fixesTasks.Any())
        {
            try
            {
                System.Threading.Tasks.Task.WaitAll(fixesTasks.ToArray());
            }
            catch { }
        }
    }

    private void FixM4AMeta(string filePath)
    {
        // Логика исправления метаданных M4A файла
        System.Diagnostics.Debug.WriteLine($"Fixing M4A metadata for {filePath}");
    }

    private string GetBaseUrl(string url)
    {
        var uri = new Uri(url);
        return $"{uri.Scheme}://{uri.Host}{uri.AbsolutePath.Substring(0, uri.AbsolutePath.LastIndexOf('/') + 1)}";
    }

    private string CombineUri(string baseUrl, string relativeUri)
    {
        if (Uri.IsWellFormedUriString(relativeUri, UriKind.Absolute))
            return relativeUri;

        if (!baseUrl.EndsWith("/"))
            baseUrl += "/";

        return baseUrl + relativeUri;
    }
}
