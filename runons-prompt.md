Starting from @merge_pdf.sh there is now a single merged_entries.json (/home/kevin/development/parsed/merged_entries.json) with all the entries in it. These entries should all be dictionary entries that follow one of the following two forms: 

1. Characters (Radical) Romanization Definition(s)
2. Romanization Characters Definition(s)

If the simplified differs from the traditional, it follows in square brackets, like this 敗 [ 败 ]. Here are some other examples of the formats:

- 敗 [ 败 ] (rad.66) bài 1. To defeat. 2. To be defeated. 3. To fail; to lose.
- bài bù 败步 Retreating step: when in hold, when you can't get in a technique, step sideways and back. From wrestling.
- bài shì 败势 Retreat to a drop stance.
- bài zhōng qǔ shèng 败中取胜 West Victory from a Defeat. 1. A tactic that gains victory from what seemed like defeat. 2. A move that turns and comes back with a strong attack. 3. In Qingping sword, a combination of a series of unpredictable high and low strikes done while stepping away, finally jumping and spinning around to a full drop stance chop.
- 扳 (rad.64) bān 1. To pull; drag. 2. A grappling technique, controlling without grabbing. One of the sixteen key techniques of Baguazhang, see also shí liù zì jué. As simplified character, also pronounced pān, to clamber, climb by pulling oneself up.
- bān shǒu 扳手 Pull, drag.

Where an entry does not follow this format and is not detected as header or footer, it is most likely a run on or continuation from the previous entry. I'd like you to add another step that will call the LLM (see parser.py for how VLLM is called) and determine whether the current entry is a continuation of the previous entry (Use the above examples to help guide the prompt to the LLM). If it is, we want to mark it as `"runOn": true` with a field `runOnFromIndex` that includes the global_index of the previous entry. Otherwise mark it as `"runOn": false`. Output the updated merged entries to a new json file with the runOn details in it called processed_entries.json.  

