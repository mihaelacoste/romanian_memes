In the context of Romania’s tense presidential elections in May 2025 - following the annulment of the 2024 elections due to foreign interference and the weaponization of TikTok - scrutinizing public participation in political debate has become even more relevant, as memes have emerged as potent tools of political expression, using humor, irony, and satire to frame narratives, mobilize voters, and potentially spread dis/misinformation (Mortensen & Neumayer, 2021).
This study examines the May 2025 ”memetic moment” (Smith & Copland, 2022) to identify dominant themes, narratives, and visual tropes in Romanian election-related memes. A sample of 703 memes, collected from the Romemes Reddit channel between May 1 and May 31, 2025, was analyzed using a multimodal approach. Deep learning models via the Gemini API were employed to detect visual elements (persons depicted, sentiment) and textual components, while semiotic analysis assessed the interplay of imagery, captions, and symbolic references in political messaging. This mixed methodology was chosen because it offers a framework for monitoring political discourse, identifying disinformation strategies, and understanding online polarization (Beskow et al., 2020).
Preliminary findings highlight three main targets of memetic attention: Elena Lasconi, runner-up in November 2024; Nicușor Dan and George Simion, both finalists in the second round in May 2025. The rivalry between Dan and Simion is often depicted as a struggle between good and evil or intelligence and ignorance, with broader implications for perceptions of their voters’ intellectual capacities. Memes also reference external actors such as Russia, Vladimir Putin, and the Pope, alongside pop culture imagery drawn from manga, cartoons, and films. By identifying relevant patterns, the study poits out how memes operate at the intersection of humor, propaganda, and political engagement in contested electoral contexts.


Methodology 

<img width="630" height="560" alt="image" src="https://github.com/user-attachments/assets/9742d5c6-471d-46e0-b8ba-3d6071dd24a4" />

This study employs a multimodal analysis approach on a visual corpus derived from the social media platform Reddit.
The corpus was sourced from relevant Romanian subreddit /romemes over May 2025. Data was collected using a custom Python script utilizing the Reddit API. The selection criteria ensured the capture of posts containing images and visual media posted between May 1 and May 31, 2025, covering the Romanian election-related memes. The final dataset comprises 703 unique political memes, forming the core analytical corpus.
Given that memes are natively multimodal (Dancygier & Vandelanotte, 2017) combining image and text/context, human coding was deemed too resource-intensive and subjective for the volume of data. Therefore, the corpus was analyzed using a Large Multimodal Model (LMM) via the Gemini API, a method known as Visual Question Answering (VQA).
Visual Question Answering (VQA) addresses answering natural-language questions grounded in visual context. While originally framed for single images, contemporary VQA generalizes to diverse visual inputs and can incorporate additional modalities. As a core vision–language problem, VQA is tightly connected to adjacent tasks from image–sentence retrieval to visual reasoning, image captioning, and visual dialog, reflecting a broader shift toward integrated multimodal understanding (Ishmam et al., 2024).
The study utilized the Gemini 2.5 Flash model (via the gemini-2.5-flash endpoint), which is optimized for high-speed, cost-effective multimodal analysis. Each meme image was ingested into the API alongside a series of highly specific, contextually engineered prompts designed to force concise, categorical output suitable for quantitative analysis:
- Who is in the image? (Key political figures, including explicit priming for Nicușor Dan, George Simion, Elena Lasconi, Traian Basescu, Marcel Ciolacu, Calin Georgescu).
- Visual Sentiment: The overall tone of the meme (e.g., Satirical, Critical, Humorous).
- Visual Characteristics: Keywords describing the aesthetic style (e.g., Photograph, Cartoon, Collage).
- Core Political Message: The main theme of the meme (e.g., Economic Failure, Anti-Corruption).
- Romanian References: Specific political parties or major events (e.g., AUR, PSD, Presidential Election).
- Text Content: Transcription of visible text.  
- The raw annotated data was then processed using the Python Pandas library to transform the comma-separated strings into quantifiable numerical metrics.

Results

<img width="878" height="518" alt="image" src="https://github.com/user-attachments/assets/5b40e412-ccff-438e-a478-d42d839969f0" />
<img width="878" height="518" alt="image" src="https://github.com/user-attachments/assets/09501964-8ad8-4798-858b-156c94c6662f" />
<img width="878" height="518" alt="image" src="https://github.com/user-attachments/assets/1709413e-13cb-40db-806b-0f9b8d0f31b1" />
