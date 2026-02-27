using BookDownloader.Models;
using BookDownloader.Drivers;
using BookDownloader.Drivers.Downloaders;

namespace BookDownloader;

public partial class MainForm : Form
{
    private List<RawBook> books;

    public MainForm()
    {
        InitializeComponent();
        InitializeBooks();
    }

    private void InitializeBooks()
    {
        books = new List<RawBook> {
            new RawBook{
                Title= "Мать ученья",
                Author= "Domagoj Kurmaic",
                SeriesName= "",
                NumberInSeries="",
                Source= new TextBook{
                    Url= "https://readli.net/mat-uchenya/",
                    Cover= "https://readli.net/wp-content/uploads/2024/02/1275666.jpg",
                    Publication= "Readli",
                    FileUrl= "https://readli.net/download.php?id=552504"
                }
            },
            new RawBook{
                Title= "Мухи",
                Author= "Айзек Азимов",
                SeriesName= "",
                NumberInSeries= "",
                Source= new AudioBook{
                    Url= "https://knigavuhe.org/book/29804-mukhi/",
                    Cover= "https://s5.knigavuhe.org/1/covers/29804/1-2.jpg?v=1",
                    Narrator= "Смолин Константин",
                    Chapters= new List<Chapter> {
                        new Chapter{
                            Title= "Мухи",
                            Url= "https://s12.knigavuhe.org/1/audio/29804/muhi-azimov.mp3",
                            FileIndex= 0,
                            StartTime= 0,
                            EndTime= 1171
                        }
                    }
                }
            }
        };

        CreateBookControls();
    }

    private void CreateBookControls()
    {
        flowLayoutPanel.Controls.Clear();

        foreach (var book in books)
        {
            var panel = new Panel
            {
                Size = new Size(350, 60),
                Margin = new Padding(3),
                BackColor = Color.LightGray // Для визуализации
            };

            var titleLabel = new Label
            {
                Text = $"{book.Title} - {book.Author}",
                Location = new Point(10, 10),
                Size = new Size(200, 40),
                Anchor = AnchorStyles.Left | AnchorStyles.Right
            };

            var downloadButton = new Button
            {
                Text = "Скачать",
                Location = new Point(250, 15),
                Size = new Size(80, 30)
            };

            downloadButton.Tag = book;
            downloadButton.Click += DownloadButton_Click;

            panel.Controls.Add(titleLabel);
            panel.Controls.Add(downloadButton);

            // Добавляем панель в FlowLayoutPanel
            flowLayoutPanel.Controls.Add(panel);
        }
    }

    private void DownloadButton_Click(object sender, EventArgs e)
    {
        var button = sender as Button;
        var book = button.Tag as RawBook;
        DownloadBook(book);
    }

    private void DownloadBook(RawBook book)
    {
        Type downloaderType = null;
        Type sourceType = null;

        if (book.Source is TextBook textBook && textBook.Url.StartsWith("https://readli.net"))
        {
            downloaderType = typeof(ZipDownloader);
            sourceType = typeof(TextBook);
        }
        else if (book.Source is AudioBook audioBook && audioBook.Url.StartsWith("https://knigavuhe.org"))
        {
            downloaderType = typeof(MP3Downloader);
            sourceType = typeof(AudioBook);
        }
        else if (book.Source is AudioBook audioBook2 && audioBook2.Url.StartsWith("https://akniga.org"))
        {
            downloaderType = typeof(M3U8Downloader);
            sourceType = typeof(AudioBook);
        }
        else
        {
            MessageBox.Show("Неподдерживаемый тип книги");
            return;
        }

        var thread = new Thread(() => _Download(downloaderType, sourceType, book));
        thread.Start();
    }

    private void _Download(Type downloaderType, Type sourceType, RawBook book)
    {
        try
        {
            var progressHandler = new DownloadProgressHandler(progressLabel);

            var constructor = downloaderType.GetConstructor(new[] { typeof(RawBook), typeof(BaseDownloadingProgressHandler) });
            var downloader = constructor.Invoke(new object[] { book, progressHandler });

            // Вызываем метод DownloadBook через reflection
            var downloadMethod = downloaderType.GetMethod("DownloadBook");
            var result = (bool)downloadMethod.Invoke(downloader, new object[] { });

            if (result)
            {
                if (progressLabel.InvokeRequired)
                {
                    progressLabel.Invoke(new Action(() =>
                        progressLabel.Text = $"Скачивание книги {book.Title} завершено"));
                }
            }
            else
            {
                if (progressLabel.InvokeRequired)
                {
                    progressLabel.Invoke(new Action(() =>
                        progressLabel.Text = $"Ошибка скачивания книги {book.Title}"));
                }
            }
        }
        catch (Exception ex)
        {
            if (progressLabel.InvokeRequired)
            {
                progressLabel.Invoke(new Action(() =>
                    progressLabel.Text = $"Ошибка: {ex.Message}"));
            }
        }
    }
}
