namespace BookDownloader.Drivers;

public enum DownloadProcessStatus
{
    Waiting,
    Preparing,
    Downloading,
    Finishing,
    Finished,
    Terminating,
    Terminated
}

public abstract class BaseDownloadingProgressHandler
{
    public DownloadProcessStatus Status { get; protected set; } = DownloadProcessStatus.Waiting;
    protected int TotalCount;
    protected int DoneCount;

    public virtual void InitStatus(DownloadProcessStatus status, int totalCount = 0)
    {
        Status = status;
        TotalCount = totalCount;
        DoneCount = totalCount == 0 ? 0 : 0;
        ShowProgress();
    }

    public virtual void Progress(int count)
    {
        DoneCount += count;
        ShowProgress();
    }

    public abstract void ShowProgress();
}

public class DownloadProgressHandler : BaseDownloadingProgressHandler
{
    private readonly System.Windows.Forms.Label label;

    public DownloadProgressHandler(System.Windows.Forms.Label label)
    {
        this.label = label;
    }

    public override void ShowProgress()
    {
        if (label.InvokeRequired)
        {
            label.Invoke(new Action(ShowProgress));
            return;
        }

        var percent = TotalCount > 0 ? Math.Round((double)DoneCount / (TotalCount / 100.0), 2) : 0;
        System.Diagnostics.Debug.WriteLine($"{Status}: {DoneCount}/{TotalCount} {percent}%");
        label.Text = $"\r{Status}: {DoneCount}/{TotalCount} {percent}%";
    }
}
