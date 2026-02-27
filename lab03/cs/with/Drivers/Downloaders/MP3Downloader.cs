using BookDownloader.Models;

namespace BookDownloader.Drivers.Downloaders;

public class MP3Downloader : BaseAudioDownloader
{
    public MP3Downloader(RawBook book, BaseDownloadingProgressHandler processHandler)
        : base(book, processHandler) { }

    protected override List<FileData> PrepareFilesData()
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
