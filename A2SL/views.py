from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from nltk.tokenize import sent_tokenize

def home_view(request):
	return render(request,'home.html')


def about_view(request):
	return render(request,'about.html')


def contact_view(request):
	return render(request,'contact.html')

@login_required(login_url="login")

def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        print(f"Received text: {text}")

        sentences = sent_tokenize(text)
        all_filtered_text = []

        for sentence in sentences:
            print(f"Processing Sentence: {sentence}")

            # Converting text to lowercase
            sentence = sentence.lower()
            text = text.lower()
            print(f"Lowercase text: {text}")

            # Tokenizing the sentence
            words = word_tokenize(sentence)
            print(f"Tokenized words: {words}")

            # POS tagging
            tagged = nltk.pos_tag(words)
            print(f"POS tagging: {tagged}")

            # Determining tense
            tense = {
                "future": len([word for word in tagged if word[1] == "MD"]),
                "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
                "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
                "present_continuous": len([word for word in tagged if word[1] in ["VBG"]])
            }
            print(f"Tense counts: {tense}")

            # Stopwords
            stop_words = set(["mightn't", ".", "?","/","!","a", "to", "the", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do',
                          "you've", 'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's",
                          "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't",
                          'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'then', 'the', 'mustn',
                           'nor', 'as', "it's", "needn't", 'd', 'am', 'have', 'hasn', 'o', "aren't",
                          "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn',
                          'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such',
                          'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn',
                          've', "isn't", "won't"])
            print(f"Stopwords list loaded.")

            # Removing stopwords and lemmatizing
            lr = WordNetLemmatizer()
            lemmatized_words = []
            for w, p in zip(words, tagged):
                if w not in stop_words:
                    if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                        lemmatized_words.append(lr.lemmatize(w, pos='v'))
                    elif p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                        lemmatized_words.append(lr.lemmatize(w, pos='a'))
                    else:
                        lemmatized_words.append(lr.lemmatize(w))

            print(f"Lemmatized words: {lemmatized_words}")

            # Adjusting words for tense
            words = lemmatized_words.copy()
            temp = ["Me" if w == "i" else w for w in words]
            words = temp

            probable_tense = max(tense, key=tense.get)
            print(f"Most probable tense: {probable_tense}")

            if probable_tense == "past" and tense["past"] >= 1:
                words.insert(0, "before")
            elif probable_tense == "future" and tense["future"] >= 1:
                if "Will" not in words:
                    words.insert(0, "will")
            elif probable_tense == "present" and tense["present_continuous"] >= 1:
                words.insert(0, "now")

            print(f"Words after tense adjustment: {words}")

            #  Re-tag POS after tense adjustment
            adjusted_tagged = nltk.pos_tag(words)
            print(f"Re-tagged POS after tense adjustment: {adjusted_tagged}")


            # Restructuring sentence after tense adjustment
            structured_words = restructure_sentence(adjusted_tagged, words)
            print(f"Words after restructuring: {structured_words}")

            # Handling animation availability
            filtered_text = []
            for w in structured_words:
                path = w + ".mp4"
                f = finders.find(path)
                if not f:
                    print(f"No video found for {w}, splitting into characters.")
                    filtered_text.extend(list(w))
                else:
                    print(f"Video found for {w}.")
                    filtered_text.append(w)

            print(f"Final words : {filtered_text}")
            all_filtered_text.append(filtered_text)
            flattened_words = [word for sentence in all_filtered_text for word in sentence]

        return render(request, 'animation.html', {'words': flattened_words, 'text': text})
    else:
        return render(request, 'animation.html')

def restructure_sentence(pos_tagged_words, words):
    subject = None
    obj = None
    verb = None
    adjective = None
    number = None
    negative = None
    question_word = None

    remaining_words = words.copy()

    for word, tag in pos_tagged_words:
        if word in remaining_words:
            if tag in ['PRP', 'NN', 'NNS'] and subject is None:
                subject = word
                remaining_words.remove(word)
            elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] and verb is None:
                verb = word
                remaining_words.remove(word)
            elif tag in ['NN', 'NNS'] and obj is None and word != subject:
                obj = word
                remaining_words.remove(word)
            elif tag in ['JJ', 'JJR', 'JJS'] and adjective is None:
                adjective = word
                remaining_words.remove(word)
            elif tag == 'CD' and number is None:
                number = word
                remaining_words.remove(word)
            elif word in ["not", "n't", "no", "never"]:  # Corrected negative handling
                negative = word
                remaining_words.remove(word)
            elif tag in ['WP', 'WRB', 'WDT'] and question_word is None:
                question_word = word
                remaining_words.remove(word)

    # Construct sentence in Subject-Object-Verb order
    reordered_words = []

    
    if subject:
        reordered_words.append(subject)

    if adjective:
        reordered_words.append(adjective)

    if number:
        reordered_words.append(number)

    if obj:
        reordered_words.append(obj)

    if negative:
        reordered_words.append(negative)

    if verb:
        reordered_words.append(verb)

    if question_word:
        reordered_words.append(question_word)  # Question words come first


    return remaining_words + reordered_words # Keep extra words at the end



def signup_view(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request,user)
			# log the user in
			return redirect('animation')
	else:
		form = UserCreationForm()
	return render(request,'signup.html',{'form':form})



def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			#log in user
			user = form.get_user()
			login(request,user)
			if 'next' in request.POST:
				return redirect(request.POST.get('next'))
			else:
				return redirect('animation')
	else:
		form = AuthenticationForm()
	return render(request,'login.html',{'form':form})


def logout_view(request):
	logout(request)
	return redirect("home")