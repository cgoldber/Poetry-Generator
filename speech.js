var synthesis = window.speechSynthesis;
var utterance = new SpeechSynthesisUtterance();

// Function to read a poem from a specific folder
function readPoemFromFolder(folderName, fileName) {
  console.log('Attempting to read poem from folder:', folderName, 'and file:', fileName);

  // Path for poem file
  var poemFilePath = 'generated_poems/' + folderName + '/' + fileName;

  // Path for article title and description files
  var titleFilePath = 'generated_poems/' + folderName + '/reference_article_title.txt';
  var descriptionFilePath = 'generated_poems/' + folderName + '/reference_article_description.txt';

  // Read article title
  var titleXhr = new XMLHttpRequest();
  titleXhr.open('GET', titleFilePath, true);
  titleXhr.onreadystatechange = function () {
    if (titleXhr.readyState == 4 && titleXhr.status == 200) {
      var articleTitle = titleXhr.responseText;
      console.log('Article Title:', articleTitle);

      // Read article description
      var descriptionXhr = new XMLHttpRequest();
      descriptionXhr.open('GET', descriptionFilePath, true);
      descriptionXhr.onreadystatechange = function () {
        if (descriptionXhr.readyState == 4 && descriptionXhr.status == 200) {
          var articleDescription = descriptionXhr.responseText;
          console.log('Article Description:', articleDescription);

          // Read poem
          var poemXhr = new XMLHttpRequest();
          poemXhr.open('GET', poemFilePath, true);
          poemXhr.onreadystatechange = function () {
            if (poemXhr.readyState == 4) {
              if (poemXhr.status == 200) {
                console.log('Poem retrieved successfully:', poemXhr.responseText);
                displayPoem(articleTitle, articleDescription, poemXhr.responseText);
                sayPoem(poemXhr.responseText);
              } else {
                console.error('Failed to retrieve poem. Status:', poemXhr.status);
              }
            }
          };
          poemXhr.send();
        }
      };
      descriptionXhr.send();
    }
  };
  titleXhr.send();
}

// Function to display the article title, description, and poem text with line breaks
function displayPoem(articleTitle, articleDescription, poemText) {
  var poemContainer = document.getElementById('poem-container');
  var lines = poemText.split('\n');

  // Clear previous content
  poemContainer.innerHTML = '';

  // Display article title
  var titleElement = document.createElement('div');
  titleElement.textContent = 'Article Title: ' + articleTitle;
  poemContainer.appendChild(titleElement);

  // Display article description
  var descriptionElement = document.createElement('div');
  descriptionElement.textContent = 'Article Description: ' + articleDescription;
  poemContainer.appendChild(descriptionElement);

  // Add a horizontal line after the description
  var hrElementDescription = document.createElement('hr');
  poemContainer.appendChild(hrElementDescription);

  // Add spacing between description and poem
  poemContainer.appendChild(document.createElement('br'));

  // Display the first line of the poem with extra spacing
  if (lines.length > 0) {
    var firstLineElement = document.createElement('div');
    firstLineElement.textContent = lines[0];
    poemContainer.appendChild(firstLineElement);
  }

  // Add a horizontal line after the first line of the poem
  var hrElement = document.createElement('hr');
  poemContainer.appendChild(hrElement);

  // Add spacing between the first line and the rest of the poem
  poemContainer.appendChild(document.createElement('br'));

  // Display the rest of the poem with a line break
  for (var i = 1; i < lines.length; i++) {
    var lineElement = document.createElement('div');
    lineElement.textContent = lines[i];

    // If the line is empty, add an extra line break for spacing
    if (lines[i].trim() === '' && i !== lines.length - 1) {
      poemContainer.appendChild(document.createElement('div'));
    }

    poemContainer.appendChild(lineElement);
  }
}


// Function to speak a given text
function sayPoem(poemText) {
  console.log('Attempting to read poem...');

  utterance.text = poemText;
  synthesis.speak(utterance);
}

// Function to stop the audio
function stopAudio() {
  console.log('Stopping audio...');
  synthesis.cancel();
}

// Function to create buttons dynamically
function createButtons() {
  var buttonContainer = document.getElementById('button-container');
  var folders = ['2023-11-19_18:17:13', '2023-11-20_20:23:17', 
  '2023-11-20_20:15:55', '2023-11-20_23:10:36', 
  '2023-11-20_23:53:43', '2023-11-21_08:26:43', '2023-11-21_09:04:57',
  '2023-11-20_15:37:29', '2023-11-21_09:31:27', '2023-11-21_10:15:17']; // Add folder names as needed

  folders.forEach(function (folderName) {
    // Read article title
    var titleFilePath = 'generated_poems/' + folderName + '/reference_article_title.txt';
    var titleXhr = new XMLHttpRequest();
    titleXhr.open('GET', titleFilePath, true);
    titleXhr.onreadystatechange = function () {
      if (titleXhr.readyState == 4 && titleXhr.status == 200) {
        var articleTitle = titleXhr.responseText;

        var button = document.createElement('button');
        button.textContent = articleTitle; // Set the button text as the article title
        button.addEventListener('click', function () {
          var fileName = 'rank_1.txt';
          readPoemFromFolder(folderName, fileName);
        });
        buttonContainer.appendChild(button);
      }
    };
    titleXhr.send();
  });

  // Create Stop button
  var stopButton = document.createElement('button');
  stopButton.textContent = 'Stop';
  stopButton.style.backgroundColor = 'red';
  stopButton.addEventListener('click', stopAudio);
  buttonContainer.appendChild(stopButton);
}

// Call createButtons to initialize the buttons
createButtons();

