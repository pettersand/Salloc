# Salloc

# Your Savings Goal Companion

Salloc is your go-to Savings Allocation app that empowers you to achieve your financial aspirations. Seamlessly allocate percentages to custom-defined categories, or "posts," and watch your savings grow purposefully. With Salloc, you can make informed spending decisions, track your progress, and ensure your funds are dedicated to what truly matters to you. Whether it's an emergency fund, a dream vacation, or a new gadget, Salloc helps you manage your savings journey with precision and purpose.

## Overview

Salloc is a free user-centric Savings Allocation app designed to empower individuals seeking a smarter way to manage and achieve their savings goals. Tailored for users who value financial discipline and goal-oriented savings, Salloc addresses the challenge of saving with purpose and clarity.

**Key Features and Benefits:**

- **Customizable Savings Posts:** Salloc enables users to create personalized savings categories, or "posts," each with its own allocated percentage. This allows users to budget effectively for specific goals and expenses.

- **Automated Fund Distribution:** With automated distribution based on allocated percentages, Salloc ensures your deposits are intelligently divided among your savings posts, giving you control and insight into your financial progress.

- **Budget-Focused Spending:** Users can make well-informed spending decisions by checking their available funds within each savings post. This prevents impulsive spending and encourages a mindful approach to personal finances.

- **Goal Tracking and Motivation:** Set savings targets, track your progress, and celebrate milestones as you move closer to achieving your financial objectives. Salloc keeps you motivated by providing clear insights into your accomplishments.

- **User-Centric Experience:** Salloc offers an intuitive and user-friendly interface, making it easy for individuals of all financial backgrounds to manage their savings with confidence.

Whether you're saving for that dream vacation, building an emergency fund, or working towards any other financial objective, Salloc empowers you to make your aspirations a reality.

## Getting Started

Simply log on or register on Salloc to start using this service!

1. Visit [Salloc](https://pettersa.com/salloc/) to access the online service.
2. Sign up for an account or log in using your existing credentials.
3. Explore the dashboard, navigation menu, and key sections to familiarize yourself with the interface. There are guided tours, a [video demo](https://www.youtube.com/watch?v=V8KPCkZ2vAs), and written explanations available.

## Features

Salloc offers a range of features designed to help users manage their savings effectively and achieve their financial goals:

- **Customizable Savings Posts:** Create personalized savings categories, such as "Emergency Fund," "Travel," "Shopping," and more. Allocate specific percentages to each post based on your financial priorities.

- **Automated Fund Distribution:** Salloc automatically distributes deposits and income to different posts according to the allocated percentages. This ensures that your funds are consistently directed toward your savings goals.

- **Budget-Focused Spending:** Stay on track with your spending by checking the available funds in each savings post. Make informed decisions about your purchases and prioritize your financial objectives.

- **Goal Tracking and Motivation:** Set savings targets for each category and track your progress over time. Salloc's visualizations and progress indicators provide motivation and encouragement to reach your financial milestones.

- **User-Centric Experience:** Salloc offers an intuitive and user-friendly interface, making it easy to create, manage, and adjust your savings categories and allocations. The app's responsive design ensures a seamless experience on both desktop and mobile devices.

- **Secure and Private:** Salloc prioritizes the security and privacy of your financial information. Your data is encrypted and stored securely, giving you peace of mind while using the app.

- **Flexibility and Control:** Enjoy the flexibility to modify your savings goals, allocations, and contributions at any time. Adapt your plan to changing financial circumstances and make adjustments as needed.

-**Dashboard - Under Development:** Features for improved visualization are underway with a reactive Dashboard at your fingertips. Create graphs and visual overviews on the savings metrics that matter to you.

-**Transaction History - Under Development:** A limited overview of your transaction history is already implemented. However this feature will be vastly improved by allowing the user to see all their account movements based on reactive menus. This will allow the user to look for patterns in their spending and saving behaviour.

Salloc empowers users to take control of their finances, make informed decisions, and work toward their financial aspirations with confidence.

## Usage

### Setting Up Savings Posts and Allocations

1. **Create Savings Posts:** After signing up and logging in, navigate to the "Setup" section. Here, you can create customized savings posts such as "Vacation," "Education," "Emergency Fund," and more.

2. **Allocate Percentages:** Assign a specific percentage to each savings post based on your financial priorities. For example, you might allocate 30% to "Vacation," 20% to "Education," and 10% to "Emergency Fund."

3. **Initial Setup:** If you want to start with a clean slate and have all your savings initially set to "Emergency Fund", simply create one post with 100%, and commit the savings. From there you can easily add posts and allocation percentages for any future deposits.

### Making Deposits and Withdrawals

1. **Record Deposits:** In the "Deposit Funds" section, enter the amount you wish to deposit. Salloc will automatically distribute the funds to each savings post according to the allocated percentages. Alternatively you may choose to deposit to a single post, or even move funds from one post to another.

2. **Withdrawals:** When spending money devoted to any given post the user can first check if they have available funds. If so, they can make a specific withdrawal from that post ensuring their savings are up to date.

### Tracking Progress and Making Decisions

1. **Monitor Available Funds:** Check the available funds in each savings post on the dashboard. This will help you make informed decisions about your spending based on your budget for each category.

2. **Visualize Progress:** Navigate to the "Overview" section to visualize your progress toward your savings targets. Visual indicators and graphs provide a clear overview of your achievements.

### Adjusting Goals and Allocations

1. **Modify Goals:** If your financial goals change, you can easily adjust your savings targets for each post. Go to the "Overview" section and update the target amounts accordingly in the tables editable fields.

2. **Update Allocations:** Update the percentage allocations for your savings posts based on your changing priorities. These adjustments will be reflected in how Salloc distributes future deposits without affecting your current savings.

### Staying Motivated

1. **Celebrate Milestones:** As you reach your savings goals, celebrate your achievements! Salloc's progress tracking and notifications will keep you motivated and up to date throughout your financial journey.

2. **Treat Yourself:** When reaching your goals you can treat yourself with a clean conscience. No more insecurity about whether you can afford something or not.

Salloc empowers you to manage your finances with precision, make deliberate choices about your spending, and achieve your financial aspirations one step at a time.

## Design Process of Salloc

1. **Initial Inspiration:** I had an old Excel spreadsheet with some of the functionalities of Salloc and found it really helped me with managing my savings. Though it had many limitations. So upon starting my programming journey I decided this would be my first full project.

2. **One Page To Rule Them All:** I wanted a dashboard-type application where the user could manage their savings and customize it to their own needs. I wanted this integrated on a single page for an improved user experience. Initially the account and home pages were separate and it lead to a confusing user experience.

3. **Dashboard:** Initially I wanted graphs integrated through Dash/Plotly right there on the main page. However it soon became clear that the functionality of the site was more important. A future implementation will give the user a reactive graph dashboard so they can better visualize their savings journey and habits.

4. **Bit Off Too Much?:** Being a man of ideas I had high aspirations for what functionalities I wanted on this site. I knew early that a SQL based database was needed, or well, I wanted one for the experience of working with SQL. I also at some point decided I wanted simple cookies. This caused a couple headaches at the time but was a valuable experience. The best, as well as worst, implementation was probably the editable overview table. It required several days of troubleshooting to fix, and I'm sure there is a better way to do it, but from a user experience point of view it is probably my favorite function on the app.

5. **Hosting:** The last headache I had to meet was finding suitable hosting for my site and portfolio through a personal domain. Since it's a flask app I needed to host it on a VPS, and configure it all with linux. Making sure the routes path was working as intended proved to be another big headache. However I got there in the end.

## Files of Salloc

1. **Python:** The backend code was written in python using Flask and a helper.py file for self written functions. App.py runs all the SQL queries and backend functions as well as routing and user feedback in the form of error messages or flash messages.

2. **Static:** I have static files, specifically images, css, and javascript files. Nothing special about these but I wanted stand-alone files to reference in my HTML. My CSS file has the styling for the entire web app. While my javascript file is mostly used for modal handling, some AJAX json forms, and sorting functionality of my tables.

3. **Templates:** The main files are my landing, layout, and index.html. Landing takes care of the login/register screen using images created through midjourney AI. Layout lays the foundation for the HTML visuals and is extended using jinja. Index is where the main program resides. All functionality starts here.

## Troubleshooting & Feedback

Please report any issues faced while using the app to me at petter.sand@gmail.com, or through the on-site "Contact Me" form. If you are having issues with your account please include your username and a valid email so I can remedy the situation. Any bug reports are highly appreciated.
If facing issues with login, try clearing your browser cache or Salloc associated cookies.

## Privacy and Security

Salloc saves no personal identifiable information. Your password is hashed and stored securely. You have full control of your account, and upon deletion EVERYTHING pertaining to your account will be permanently deleted. Salloc stores no other information about you than what you can see in your account. No third parties receive any of your information or habits. The creator of Salloc may in the future use user statistics to improve the site and to maintain a seamless lag-free service.

## About

My name is Petter Sand Austnes. After 13 years as a strength coach and personal trainer I found love on a different path. Salloc is an improved implementation of an excel spreadsheet I had been using privately. And thus, my first project on my software development journey. I had been coding for just over 3 months at the launch of Salloc. So I assume it will only get better with time. I hope you will enjoy and find a use for this application, and that it may help you reach your savings goals!

[GitHub Profile](https://github.com/pettersand)
[Portfolio Website](https://pettersa.com)

---

**Note:** This README is intended to provide an overview of the user-experience of the service. This project is not intended for open-source development at the moment. Though any feedback, ideas, wishes to contribute will be taken into account.
