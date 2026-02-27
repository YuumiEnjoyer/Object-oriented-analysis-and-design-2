using BookDownloader.Models;

namespace BookDownloader.Drivers;

public class FileData
{
    public int Index { get; set; }
    public string Name { get; set; }
    public string Url { get; set; }
    public int? Size { get; set; }
    public Dictionary<string, object> Extra { get; set; }

    public FileData(int index, string name, string url, int? size = null)
    {
        Index = index;
        Name = name;
        Url = url;
        Size = size;
        Extra = new Dictionary<string, object>();
    }
}

public abstract class BaseDownloader<T> where T : BookSource
{
    protected RawBook Book;
    protected T Source;
    protected Dictionary<int, string> DownloadedFiles;
    protected BaseDownloadingProgressHandler ProcessHandler;
    protected HttpClient HttpClient;
    protected bool Terminated;
    protected List<FileData> Files;
    protected int TotalSize;

    public BaseDownloader(RawBook book, BaseDownloadingProgressHandler processHandler)
    {
        Book = book;
        Source = book.Source as T ?? throw new InvalidOperationException(
                $"Cannot cast Source of type {book.Source?.GetType()} to {typeof(T)}");
        DownloadedFiles = new Dictionary<int, string>();
        ProcessHandler = processHandler;
        HttpClient = new HttpClient();
        Files = new List<FileData>();
        Terminated = false;
        TotalSize = 0;
    }

    public BaseDownloadingProgressHandler ProcessHandlerProperty => ProcessHandler;
    public abstract bool DownloadBook();
}

public abstract class BaseAudioDownloader : BaseDownloader<AudioBook>
{
    public BaseAudioDownloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler) { }
}

public abstract class BaseTextDownloader : BaseDownloader<TextBook>
{
    public BaseTextDownloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler) { }
}
