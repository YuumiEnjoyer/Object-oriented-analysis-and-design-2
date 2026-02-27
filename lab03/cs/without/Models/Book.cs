namespace BookDownloader.Models;

public class Chapter
{
    public string Title { get; set; }
    public string Url { get; set; }
    public int FileIndex { get; set; }
    public int StartTime { get; set; }
    public int EndTime { get; set; }

    public int Duration => EndTime - StartTime;
}

public abstract class BookSource
{
    public string Url { get; set; } = "";
    public string Cover { get; set; } = "";

    public abstract string DirPath { get; }
    public virtual string CoverPath => "cover.jpg";
}

public class TextBook : BookSource
{
    public string Publication { get; set; }
    public string FileUrl { get; set; }

    public override string DirPath => ".";
}

public class AudioBook : BookSource
{
    public string Narrator { get; set; }
    public List<Chapter> Chapters { get; set; } = new List<Chapter>();

    public override string DirPath => Path.Combine(".", Narrator);
}

public class BookData
{
    public string Title { get; set; }
    public string Author { get; set; }
    public string SeriesName { get; set; }
    public string NumberInSeries { get; set; }

    public string BookPath
    {
        get
        {
            var path = Path.Combine(".", Author);
            if (!string.IsNullOrEmpty(SeriesName))
            {
                var bookName = $"{NumberInSeries.PadLeft(2, '0')}. {Title}";
                path = Path.Combine(path, SeriesName, bookName);
            }
            else
            {
                path = Path.Combine(path, Title);
            }
            return path;
        }
    }

    public string DirPath
    {
        get
        {
            var booksFolder = Environment.GetEnvironmentVariable("books_folder");
            return Path.GetFullPath(Path.Combine(booksFolder, BookPath));
        }
    }

    public string CoverPath => Path.Combine(DirPath, "cover.jpg");
}

public class RawBook : BookData
{
    public BookSource Source { get; set; }

    public string DirPath => Path.Combine(base.DirPath, Source.DirPath);
}
