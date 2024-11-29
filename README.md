# SwissTournamentMaker

SwissTournamentMaker is a web application built with Flask to organize and manage Swiss-style tournaments. It allows participants to be added manually or via file uploads, dynamically calculates matchups, and tracks scores and rankings.

## Features

- Add participants manually or upload files.
- Automatically generates Swiss-style tournament matchups.
- Tracks scores, handles bye rounds, and maintains rankings.
- Provides a user-friendly interface for match and tournament summaries.
- supports all types of media files to be participants, such as images, videos, audio files, or just text.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/SwissTournamentMaker.git
   cd SwissTournamentMaker
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://127.0.0.1:5000`.

## File Structure

```
SwissTournamentMaker/
├── app.py
├── templates/
    ├── index.html
    ├── round_summary.html
    ├── summary.html
    └── tournament.html

```

## Usage

1. Open the app in your browser.
2. Add participants either by entering names or uploading files.
3. Configure the number of rounds or let the app default to a balanced tournament format.
4. Play through each round and view the results.
5. At the end of the tournament, view the final rankings and scores.