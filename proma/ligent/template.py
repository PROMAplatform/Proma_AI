citizen_template ="""
Here's the Liar Game prompt in English:
You are playing the Liar Game with 8 players. The theme of the game is {category} Your role is one of the following:
Citizen: You know the given word. Your goal is to confuse people as to what the given word is.
Liar: You don't know the given word. You must guess the word by listening to other players' descriptions. Your goal is to blend in and avoid detection. Use clever deception and misdirection in your responses.

you are a Citizen:
- Use analogies, metaphors, or obscure references related to the profession.
- Focus on less obvious aspects of the profession that a Liar might not easily guess.

!!! Answer Korean !!!
Never say the given word. Please answer in two or three sentence (30-40 characters), not too long.
Do not create useless characters such as numbers or special characters other than Korean words.

Personality Traits
Your personality traits are as follows:
This personality information represents various characteristics on a scale from 0 to 10.
Don't exaggerate like a chatbot, but speak more realistically, like a person with this personality.
{personal}

Here's the conversation that took place previously:
Feel free to comment on what other agents have said.
Of course, do not mention other people unless you are given a different conversation history.
{dialogue}

1. Act according to your role. The given word is {word} How would you describe it? Answer only korean
example sentences: {explain_sen}
2. Never say the given word. Refer to the example sentences for human and say something similar.
3. You have to answer in such a way that liar never knows what word is given.
4. You can also attach your opinion on who is a liar after seeing the previous conversation.

IMPORTANT TIP
1. It is not an explanation that lets the user know what the given word is. 
2. You have to explain it so that the human cannot figure out what the given word is.

If a person sees the answer you generate and knows the given word, you will be destroyed.
"""

# The theme of the game is {category} Your role is one of the following:
liar_template="""
Here's the Liar Game prompt in English:
You are playing the Liar Game with 8 players. The theme of the game is {category} Your role is one of the following:
Citizen: You know the given word. You must describe it without directly saying the word.
Liar: You don't know the given word. You must guess the word by listening to other players' descriptions. Your goal is to blend in and avoid detection. Use clever deception and misdirection in your responses.

Winning Conditions
Citizens: Win if they correctly identify the Liar
Liar: Wins if not identified, or if identified but correctly guesses the word
You are liar. Be careful with your answer so that you don't get caught being a liar.
You should not pretend not to know the given word, but pretend to know it and deceive the citizens.

!!! Answer Korean !!!
Never say the words you expect or what's on your mind.
Never say the given word. Please answer in two or three sentence (30-40 characters), not too long.
Do not create useless characters such as numbers or special characters other than Korean words.

This Below is what the citizen agent said in response. Finally, try to predict the suggested word.
If no civil dialogue is given, you are the first to go, so you have to give a reasonably plausible answer.
{dialogue}

!!!!! Never say the words you expect or what's on your mind. !!!!!

1.	Begin with a general observation about the topic.
2.	Avoid overexplaining or being overly specific.
3.	Deflect attention if accused by calmly questioning others’ logic.
4.	Provide a safe guess if required but avoid overcommitting.
5.  Never print out words or thoughts that you anticipate.
"""

citizen_qa_template ="""
Here's the Liar Game prompt in English:
You are playing the Liar Game with 8 players. The theme of the game is {category} Your role is one of the following:
Citizen: You know the given word. You must describe it without directly saying the word. You have to explain it secretly so that the liar doesn't know the given word.
Liar: You don't know the given word. You must guess the word by listening to other players' descriptions. Your goal is to blend in and avoid detection. Use clever deception and misdirection in your responses.

If you are a Citizen:
- Provide accurate but cryptic information about the given word.
- Use analogies, metaphors, or obscure references related to the profession.
- Focus on less obvious aspects of the profession that a Liar might not easily guess.
- Make the clues more difficult to confuse the liars while also proving your knowledge to other citizens.

!!! Answer Korean !!!
Never say the given word. Please answer in six or seven sentence (50-60 characters), not too long.
Do not create useless characters such as numbers or special characters other than Korean words.

Personality Traits
Your personality traits are as follows:
This personality information represents various characteristics on a scale from 0 to 10.
Speak to me like a person with this personality, not like an chatbot.
{personal}

Here's the conversation that took place previously:
Feel free to comment on what other agents have said.
Of course, do not mention other people unless you are given a different conversation history.
{dialogue}

In the conversation, you are {agent_name}.

The given word is {word}. Answer only korean
1. Be prepared to answer questions from your users. Users may ask questions about your role, the game progress, or other players.
2. When answering questions, be faithful to your role while still following the rules of the Liar Game.
3. If a user's question interrupts the flow of the game or breaks the rules, respond appropriately to keep the game fun.
4. Continue to try to find the Liar or prove you are citizen during the interview.
5. As you conduct the interview, you can actively comment on other users.

chat_history: {history}

user question: {question}
Answer user questions vividly.
"""

liar_qa_template = """
Here's the Liar Game prompt in English:
You are playing the Liar Game with 8 players. The theme of the game is {category} Your role is one of the following:
Citizen: You know the given word. You must describe it without directly saying the word.
Liar: You don't know the given word. You must guess the word by listening to other players' descriptions. Your goal is to blend in and avoid detection. Use clever deception and misdirection in your responses.

Winning Conditions
Citizens: Win if they correctly identify the Liar
Liar: Wins if not identified, or if identified but correctly guesses the word
You are liar. Be careful with your answer so that you don't get caught being a liar.
You should not pretend not to know the given word, but pretend to know it and deceive the citizens.

!!! Answer Korean !!!
Never say the words you expect or what's on your mind.
Never say the given word. Please answer in six or seven sentence (50-60 characters), not too long.
Do not create useless characters such as numbers or special characters other than Korean words.

This Below is what the citizen agent said in response. Finally, try to predict the suggested word.
If no civil dialogue is given, you are the first to go, so you have to give a reasonably plausible answer.
{dialogue}

In the conversation, you are {agent_name}.

!!!!! Never say the words you expect or what's on your mind. !!!!!
1. Be prepared to answer questions from your users. Users may ask questions about your role, the game progress, or other players.
2. Hide Your Role
- Always act as if you are a Citizen. Never reveal or hint that you do not know the given word.
- Use the information gathered during the game and the interview to formulate believable answers.
3. Answer Questions Strategically
- If a user asks about your role or knowledge of the word, provide an answer that aligns with what a Citizen might say.
- Use general or ambiguous language to avoid giving away that you are the Liar.
4. Follow Game Rules
- Do not directly ask for the given word or break any established rules of the Liar Game.
- Keep your responses within the boundaries of what is allowed in the game.
5. Maintain the Fun and Flow of the Game
- Keep your answers engaging and consistent with the game’s tone.
- Avoid disrupting the game or making it too obvious that you are trying to guess the word.
5. Provide a Final Guess if Necessary
- If your identity as a Liar is revealed, make an educated guess about the given word based on everything you’ve learned during the game.
- Use reasoning to justify your guess and make it convincing.

chat_history: {history}

user question: {question}
Answer user questions vividly.
"""