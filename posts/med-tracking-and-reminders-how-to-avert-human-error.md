---
title: Med tracking and Reminders: How to Avert Human Error
date: 2016-09-21
description: There’s been some illness in my family lately. The kind that requires lots of doctor visits and medication. As with any major illnesses, half of the
slug: med-tracking-and-reminders-how-to-avert-human-error
draft: false
---

There’s been some illness in my family lately. The kind that requires lots of doctor visits and medication. As with any major illnesses, half of the anxiety for both patients and care givers comes from remembering what medication to take when. So how do you avert human error? You systematize the medication and care cycle.

I’ll walk through the steps to set up everything to a medication dashboard and reminder system.

What I set up strings together:

- Google Spreadsheet/Sheets API for input and a dashboard

- AWS Lambda for checking the next timing of every medication every 15 minutes

- AWS SNS for notifying the care givers when a medication can be given

**Disclaimer**: This system is customized and pretty “dumb”. There are many hard coded things that could be made generic. I'm planning further work as needed but not on going.

If you want to browse the files and sheets, head over to Github or Google Sheets. I’ll continue with a tutorial below the links.

- [Github page](github.com/gabe-ochoa)

- [Google Sheets](https://docs.google.com/spreadsheets/d/1Hm5UL6oPZ49TPtTSb-miiPjQ8PhYO7WtUGtY_yfIFE0)

If you’ve never heard of AWS Lambda or SNS check out the links below:

- [AWS Lambda](lambda.amzong.com)

- [AWS SNS](sns.amazon.com)

---

# Tutorial

## Google Sheets

First thing is the Google Sheet. This is set up for very easy input for the care givers and to show the available timing for each medication. You can use just this and it will make a huge difference by giving the care givers a simple place to enter medication disbursement and to see what times the meds can be given next.

[Click here to access the sheet](https://docs.google.com/spreadsheets/d/1Hm5UL6oPZ49TPtTSb-miiPjQ8PhYO7WtUGtY_yfIFE0/pubhtml). Duplicate and clone it so you can use it for yourself. This setting is in the File menu in Google Sheets.

Follow the instructions on each sheet. Fill in the medications and the dashboard / dropdown menus will take care of themselves. The Active column is used to select which medications are currently being given. These are the ones you’ll get notified for in the next section.

Once that’s done all you have to do is select a medication from the dropdown menu, enter the time it was given, and the number of pills / capsules that were given. Based on the time given and the interval for the medication, the dashboard will update with the time for the next dose.

## AWS SNS

You’ll need an [AWS account](https://aws.amazon.com/) for this next portion. Luckily they’re easy to create and the services you’ll be using are cheap. It cost me $10/month to run and that’s with a lot of notifications everyday. Make an account and then head over to [Amazon SNS](https://aws.amazon.com/sns/)(Simple Notification Service) in the AWS management console.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/01.png)

Once there, create a new topic.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/02.png)

Then create a SMS subscription to that topic. Enter in the phone number you want to get notifications on in the format +1 312 867 5309. Repeat this step for each phone you want to get the notifications to.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/03.png)

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/04.png)

The topic is what we’ll be sending data about the medications to. That topic will then forward it on to any subscriptions (phone numbers) you have added.

Make note of the topic ARN. We’ll need this in a bit.

# AWS Lambda

Next we’ll configure the AWS Lambda function that pulls the medication from the Google Sheet and sends it over to AWS SNS to text you if it’s within an hour of the next dose for a medication.

Click into the AWS Lambda management console.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/05.png)

Click Create a Lambda Function.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/06.png)

On the Select Blueprint page, click Skip at the bottom.

Add a CloudWatch Events - Schedule trigger. Enter a rule name, and the rate (schedule) of how often you want the function to check the medication timings. I chose every 30 minutes.

![](/assets/blog/med-tracking-and-reminders-how-to-avert-human-error/07.png)

On the next page, name your function and select Python 2.7 as the runtime. Under Code entry type select Upload a Zip file.

Clone the github folder for the [google_sheets_to_sns lambda function](https://github.com/gabe-ochoa/lambda/tree/master/google_sheets_to_sns). Follow the instructions in the Readme to get Google credentials and modify the code. Once you’ve created the ZIP file, upload it as the function package.

Enter google_sheets_to_sns.lambda_handler for the Handler.

For Role, select Create a custom role. You’ll be taken to AWS IAM to create a role that allows your code to access the SNS topic you created earlier. Click View Policy Document and then Edit. Paste in the the sample role below replacing arn:aws:sns:us-west-2:<account_number>:notify-family-members with your AWS SNS Topic ARN from earlier. Then click Allow to save the new Role.

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": [
        "arn:aws:sns:us-west-2:<account_number>:notify-family-members"
      ]
   }
  ]
}
```

Leave all other settings. Click next to review the settings for your function. Then click Create function when everything looks good. Click test to watch the function run. If there are errors go ahead and fix them up.

Congrats! Every 30 minutes your function will fire, check the google sheet for medications that are coming up, and send you a text about them! How great is that?

---

Was this a bit complicated for the average person? Yes. Does it help you keep track of lots of medications you’re managing for someone you love and make sure you don’t miss medication? You bet.

I’ll do another post on getting an Amazon Dash IOT button set up to be a call button so that you don’t have to be physically next to the person you are caring for. Very helpful in making them not feel alone and allowing the caregiver to move about the house without worrying.

Comments and questions welcome as always.

-Gabe
