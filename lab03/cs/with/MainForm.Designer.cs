using System.Windows.Forms;

namespace BookDownloader;

partial class MainForm : Form {
    private FlowLayoutPanel flowLayoutPanel;
    private Label progressLabel;

    private void InitializeComponent() {
        this.flowLayoutPanel = new FlowLayoutPanel();
        this.progressLabel = new Label();
        this.SuspendLayout();

        //
        // flowLayoutPanel
        //
        this.flowLayoutPanel.AutoScroll = true;
        this.flowLayoutPanel.Dock = DockStyle.Fill;
        this.flowLayoutPanel.Location = new System.Drawing.Point(0, 0);
        this.flowLayoutPanel.Name = "flowLayoutPanel";
        this.flowLayoutPanel.Size = new System.Drawing.Size(400, 250);
        this.flowLayoutPanel.TabIndex = 0;

        //
        // progressLabel
        //
        this.progressLabel.Dock = DockStyle.Bottom;
        this.progressLabel.Location = new System.Drawing.Point(0, 250);
        this.progressLabel.Name = "progressLabel";
        this.progressLabel.Size = new System.Drawing.Size(400, 30);
        this.progressLabel.Text = "";
        this.progressLabel.TextAlign = ContentAlignment.MiddleLeft;

        //
        // MainForm
        //
        this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
        this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        this.ClientSize = new System.Drawing.Size(400, 280);
        this.Controls.Add(this.flowLayoutPanel);
        this.Controls.Add(this.progressLabel);
        this.Name = "MainForm";
        this.Text = "Book Downloader";
        this.ResumeLayout(false);
    }
}
