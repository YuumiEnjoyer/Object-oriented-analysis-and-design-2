using System;
using System.Windows.Forms;

namespace BookDownloader;

internal static class Program
{
    [STAThread]
    static void Main()
    {
        Environment.SetEnvironmentVariable("books_folder", "../../downloads");

        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new MainForm());
    }
}
