using System;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using System.Windows.Forms;
using WatsonWebsocket;
using System.Linq;

namespace AutoDoor
{
    public partial class Form2 : Form
    {
        private JObject configP;
        private WatsonWsClient wsc2;
        public Form2(string config,WatsonWsClient wsc)
        {
            wsc2 = wsc;
            configP = JObject.Parse(config);
            InitializeComponent();
        }

        private void Form2_Load(object sender, EventArgs e)
        {
            List<string> nMin = new List<string> { };
            foreach (string item in new string[] { "startmin", "endmin", "lstartmin", "lendmin" })
            {
                int temp = int.Parse(configP.SelectToken(item).ToString());
                if (temp < 10){nMin.Add($"0{configP.SelectToken(item)}");}else{nMin.Add(configP.SelectToken(item).ToString());}
            }
            SchoolStart.Text = $"{configP.SelectToken("starth")}:{nMin[0]}";
            SchoolEnd.Text = $"{configP.SelectToken("endh")}:{nMin[1]}";
            LunchStart.Text = $"{configP.SelectToken("lstarth")}:{nMin[2]}";
            LunchEnd.Text = $"{configP.SelectToken("lendh")}:{nMin[3]}";
            LedPin.Text = $"{configP.SelectToken("LEDPin")}";
            ServoPin.Text = $"{configP.SelectToken("ServoPin")}";
            string[] test = configP.SelectToken("list").ToString().Split(',');
            foreach(string student in test)
            {
                richTextBox1.Text += student + "\n";
            }
            
        }


        private void button2_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            DialogResult dialogResult = MessageBox.Show("Are you sure you want to update AutoDoor config?\nThis will overwite existing settings", "Security Check", MessageBoxButtons.YesNo);
            if (dialogResult == DialogResult.No) return;
            string check = "";
            button2.Enabled = false;button1.Enabled = false;
            string start = TimeCheck(SchoolStart.Text);
            if (start == "failed" || start == "false"){check += "Bad School Start time\n";}
            string end = TimeCheck(SchoolEnd.Text);
            if (end == "failed" || end == "false"){check += "Bad School End time\n";}
            string lstart = TimeCheck(LunchStart.Text);
            if (lstart == "failed" || lstart == "false"){check += "Bad Lunch Start time\n";}
            string lend = TimeCheck(LunchEnd.Text);
            if (lend == "failed" || lend == "false"){check += "Bad Lunch End time\n";}
            if (check != "")
            {
                MessageBox.Show(check);
                button2.Enabled = true;button1.Enabled = true;
                return;
            }
            int servo;int led;
            try { servo = int.Parse(ServoPin.Text); } catch { MessageBox.Show("Invaild Servo pin number"); button2.Enabled = true; button1.Enabled = true; return; }
            try { led = int.Parse(LedPin.Text); } catch { MessageBox.Show("Invaild LED pin number"); button2.Enabled = true; button1.Enabled = true; return; }
            string muddystudent = richTextBox1.Text;
            foreach (string item in new string[] {",","\"","\'","ß","[","]","{","}" }){
                muddystudent = muddystudent.Replace(item, string.Empty);
            }
            string[] dirtystudent = muddystudent.Split('\n');
            List<string> cleansudent = new List<string> { };
            foreach (string stud in dirtystudent){if (stud != ""){cleansudent.Add(stud);}}
            string student = string.Join(",", cleansudent);
            string newJson = $"{{'starth':{int.Parse(start.Split(',')[0])},";
            newJson += $"'endh':{int.Parse(end.Split(',')[0])},";
            newJson += $"'startmin':{int.Parse(start.Split(',')[1])},";
            newJson += $"'endmin':{int.Parse(end.Split(',')[1])},";
            newJson += $"'lstarth':{int.Parse(lstart.Split(',')[0])},";
            newJson += $"'lstartmin':{int.Parse(lstart.Split(',')[1])},";
            newJson += $"'lendh':{int.Parse(lend.Split(',')[0])},";
             newJson += $"'lendmin':{int.Parse(lend.Split(',')[1])},";
            newJson += $"'LEDPin': {led},";
            newJson += $"'ServoPin': {servo},";
            newJson += $"'logFile': '{configP.SelectToken("logFile")}',";
            newJson += $"'list':'{student}'}}";

            wsc2.SendAsync($"updateConfigß{newJson.Replace('\'', '"')}");
        }

        private void SchoolStart_TextChanged(object sender, EventArgs e)
        {

        }

        private string TimeCheck(string time)
        {
            string[] temp = new string[] { };
            int hour;int min;
            if (time.Contains(":")){
                temp = time.Split(':');
            }
            else{try{temp = (string[])SplitC(time, 2);}catch{return "failed";}}
            try{hour = int.Parse(temp[0]);min = int.Parse(temp[1]);}catch{return "failed";}
            if((hour >= 0 && hour < 24)&&(min >= 0 && min < 60)){return $"{hour},{min}";}
            return "false";
        }
        static IEnumerable<string> SplitC(string str, int chunkSize)
        {
            return Enumerable.Range(0, str.Length / chunkSize)
                .Select(i => str.Substring(i * chunkSize, chunkSize));
        }
    }
}
