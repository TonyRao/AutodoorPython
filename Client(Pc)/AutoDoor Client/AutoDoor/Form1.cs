using System;
using System.Windows.Forms;
using WatsonWebsocket;
using System.Text;

namespace AutoDoor
{
    public partial class Form1 : Form
    {
        // this was written very poorly don't blame us. our hands were forced by shitty microsft .net shit
        WatsonWsClient wsc = new WatsonWsClient("192.168.12.5", 8765, false);
        public static Form2 frm2;
        public static string incomArg = "";
        public static string incomData = "";
        public static string status = ""; 
        public Form1()
        {
            InitializeComponent();
        }
        static void MessageReceived(object sender, MessageReceivedEventArgs args) // don't bother running stuff here as it won't work 99% of the time
        {
            string serverData = Encoding.UTF8.GetString(args.Data);
            if (!serverData.Contains("ß")) // looks for ß and splits it if not found returns and displays message
            {
                incomArg = serverData; return;
            }
            incomArg = serverData.Split('ß')[0];incomData = serverData.Split('ß')[1];
        }
        static void ServerConnected(object sender, EventArgs args) // don't bother running here as well as its in a dif thread
        {
            status = "Server Connected";
        }
        static void ServerDisconnected(object sender, EventArgs args)// same here
        {
            status = "Server Disconnected";
        }
        private void Form1_Load(object sender, EventArgs e)
        {
            //nothing
        }
        private void Form1_Shown(Object sender, EventArgs e)
        {
            wsc.Start();wsc.ServerConnected += ServerConnected;wsc.ServerDisconnected += ServerDisconnected;wsc.MessageReceived += MessageReceived;
        }
        private void StartBtn_Click(object sender, EventArgs e)
        {
            disableAll();wsc.SendAsync("startAutodoor");
        }
        private void StopBtn_Click(object sender, EventArgs e)
        {
            disableAll();wsc.SendAsync("stopAutodoor");
        }

        private void UpdateBtn_Click(object sender, EventArgs e)
        {
            disableAll();wsc.SendAsync("getConfig");
        }

        private void richTextBox1_TextChanged(object sender, EventArgs e)
        {
            // scroll it automatically
            richTextBox1.SelectionStart = richTextBox1.Text.Length;richTextBox1.ScrollToCaret();
        }

        private void LogBtn_Click(object sender, EventArgs e)
        {
            disableAll();wsc.SendAsync("getLogs");
        }

        private void EventTimer_Tick(object sender, EventArgs e)
        {
            MessageBox.Show("Operation failed | took too long");enableAll();
        }

        private void UpdateTimer_Tick(object sender, EventArgs e)    // update every sec and checks if vars are there and executes commands
        {
            if (status != "")
            {
                textBox1.Text = status;
                if(status == "Server Disconnected")
                {
                    StartBtn.Enabled = false;StopBtn.Enabled = false;UpdateBtn.Enabled = false;LogBtn.Enabled = false;ReconnectBtn.Enabled = true;
                }
                else if(status == "failed to connect"){ConnectionTimer.Enabled = false;ReconnectBtn.Enabled = true;}
                else{ConnectionTimer.Enabled = false;ReconnectBtn.Enabled = true;StartBtn.Enabled = true;StopBtn.Enabled = true;UpdateBtn.Enabled = true;LogBtn.Enabled = true;}
                status = "";
            }
            if (incomArg == "") return;
            string msgbox = incomArg;string msgboxD = incomData;
            enableAll();
            if (incomArg == "Logs")
            {
               string[] parsedD = incomData.Split('\n');string newout = "";int count = 0;richTextBox1.Text = "";
               foreach(string line in parsedD)  // This is bad, very bad! this is need to push logs to richtextbox
                {                               // in chuncks if you push in full it cuts it off text
                    newout += line +"\n";
                    if(count++ == 150){richTextBox1.Text += newout;newout = "";count = 0;}
               }
                richTextBox1.Text += newout;
                incomArg = ""; incomData = "";
                return;
            }else if (incomArg == "config updated")
            {
                incomArg = ""; incomData = "";
                MessageBox.Show(msgbox);
                frm2.Close();
            }
            else if(incomArg == "config")
            {
                frm2 = new Form2(incomData,wsc);
                incomArg = "";incomData = ""; // don't judge me (required to stop loop) 
                frm2.ShowDialog();
                return;
            }
            else if (incomArg == "Bad Command")
            {
                incomArg = ""; incomData = "";
                MessageBox.Show(msgboxD);
            }else if (msgboxD != "")
            {
                incomArg = ""; incomData = "";
                if(msgboxD == "updateConfig") { try { frm2.Close(); } catch { } }
                MessageBox.Show($"{msgbox}: {msgboxD}");
            }
            else
            {
                incomArg = "";MessageBox.Show(msgbox);
            }
            incomArg = "";incomData = "";
        }

        public void disableAll()
        {
            StartBtn.Enabled = false;StopBtn.Enabled = false;UpdateBtn.Enabled = false;LogBtn.Enabled = false;EventTimer.Enabled = true;
        }
        private void enableAll()
        {
            StartBtn.Enabled = true;UpdateBtn.Enabled = true;StopBtn.Enabled = true;LogBtn.Enabled = true;ReconnectBtn.Enabled = true;EventTimer.Enabled = false;
        }

        private void ReconnectBtn_Click(object sender, EventArgs e)
        {
            ReconnectBtn.Enabled = false;textBox1.Text = "reconnecting...";ConnectionTimer.Enabled = true;
            try{wsc.Stop();}catch{/*idk what to put here (for good practice you need to kill the connection even if its dead)*/}
            wsc = new WatsonWsClient("192.168.12.5", 8765, false);
            wsc.Start();wsc.ServerConnected += ServerConnected; wsc.ServerDisconnected += ServerDisconnected; wsc.MessageReceived += MessageReceived;
        }

        private void ConnectionTimer_Tick(object sender, EventArgs e)
        {
            status = "failed to connect";
        }

        private void Form1_Resize(object sender, EventArgs e)
        {
            richTextBox1.Height = this.Height - 310;
        }
    }
}