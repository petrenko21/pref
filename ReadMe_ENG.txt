
--------------------------------------------------------------------------------------------------

Python Pref 2.34 build 4 (PyPref)

--------------------------------------------------------------------------------------------------

Python Pref's source code is based on kpref by Azarniy I.V. and OpenPref (http://openpref.narod.ru).

Author (version 2.0): Alexander aka amigo <amigo12@newmail.ru> - Aug 2007
Versions 2.1-2.34: Vadim Zapletin <preference.gixx@mail.ru> - Feb-Mar 2018
License: GNU GPL

--------------------------------------------------------------------------------------------------

Python Pref (PyPref) is a card game Preference written in the Python programming language.

For some time Python Pref (PyPref) existed only in a version for Symbian OS smartphones. Now, this version of the game is also available for Windows and all devices where Python with Tkinter graphical environment is installed. This can be both personal computers and various PDAs with ARM processor architecture working under control of Microsoft Windows CE based OS (PocketPC, Windows Mobile, etc.).

The game supports QVGA and VGA screen resolutions or window sizes and two desk orientations: portrait and landscape.

--------------------------------------------------------------------------------------------------

Changes in version 2.34 build 4

--------------------------------------------------------------------------------------------------

The file ÏÐÀÂÈËÀ_ÈÃÐÛ_Â_ÏÐÅÔÅÐÀÍÑ_(Preference_rules_in_Russian).docx has been updated.

--------------------------------------------------------------------------------------------------

Changes in version 2.34 build 3

--------------------------------------------------------------------------------------------------

Some errors in the document ÏÐÀÂÈËÀ_ÈÃÐÛ_Â_ÏÐÅÔÅÐÀÍÑ_(Preference_rules_in_Russian).docx have been corrected.

--------------------------------------------------------------------------------------------------

Changes in version 2.34 build 2

--------------------------------------------------------------------------------------------------

The file ÏÐÀÂÈËÀ_ÈÃÐÛ_Â_ÏÐÅÔÅÐÀÍÑ_(Preference_rules_in_Russian).docx, which is in the program's folder, has been updated.

--------------------------------------------------------------------------------------------------

Changes in version 2.34

--------------------------------------------------------------------------------------------------

The algorithm of whisting on 10 contracts has been corrected.

--------------------------------------------------------------------------------------------------

Changes in version 2.33

--------------------------------------------------------------------------------------------------

Wrong 'Here' ('The same') bids have been corrected.

--------------------------------------------------------------------------------------------------

Changes in version 2.32

--------------------------------------------------------------------------------------------------

1. The algorithm of whisting on 10 contracts has been improved.

2. A number of coins appearing at the end of a game has been limited (an unlimited number led to temporary hanging of the application and long waiting for the end of the procedure).

3. The height of the pool's canvas has been reduced to see the tricks' counter in full in the portrait layout at the end of a deal.

--------------------------------------------------------------------------------------------------

Changes in version 2.31

--------------------------------------------------------------------------------------------------

The joystick has been enlarged.

--------------------------------------------------------------------------------------------------

Changes in version 2.3

--------------------------------------------------------------------------------------------------

1. Correction of penalty recordings for two players whisted, when they don't fulfil their collective obligations.
2. Changing conventions during a game is not allowed now.
3. The 'Exit' option has been removed from the 'Score' and 'About' windows.

--------------------------------------------------------------------------------------------------

Changes in version 2.2

--------------------------------------------------------------------------------------------------

A new algorithm of whisting on 10 contracts has been added.

--------------------------------------------------------------------------------------------------

Differences between 2.1 and 2.0 versions

--------------------------------------------------------------------------------------------------

In version 2.1, the below stated critical bugs were fixed (they are not related to the AI decision-making algorithms).

--------------------------------------------------------------------------------------------------

The bugs found in version 2.0:

1. Regardless of the chosen variant of Preference (Sochi/Leningrad/Rostov), the Leningrad scoring rules are applied, according to which 1 pool point equals 20 whists, whereas in the Sochi and Rostov variants it should be equal to 10 whists.

2. Whists obtained as a result of an all-pass game in the Rostov variant are not added in the accumulative way.

3. The Gentleman Whist rule is not followed in the Leningrad and Rostov variants. Also, a total amount of whists to be written by the rule is not correct.

4. In the Sochi and Rostov variants, when it is impossible to record pool points as an "aid", they are recorded as 5 whists per 1 pool point against each opponent of the player that earned them, although 1 pool point should be equal to about 3 whists (that is 10 divided by 3).

5. In the Leningrad variant, when a player failed to fulfill his contract, he gets the amount of mountain points equal to the value of the game, however, according to the convention, the amount must be doubled.

6. The Options '10 tricks > Whisted' and '10 tricks > Checked' work incorrectly, that is in the opposite way.

7. When 10 contracts are supposed to be whisted, the AI players always pass. P.S. There was a bug in the source code, which led to 2 passes on 10 contracts.

8. The 'HalfWhist' option doesn't work.

9. When 10 contracts are checked and a player who declared the contract takes all 10 tricks, the opponent on his right gets 10 mountain points (whereas the player that won the game, in due order, gets 10 pool points). So, the source code function, which scores penalty points in accordance with the rule 'The second player whisted is responsible', works incorrectly.

10. In the Leningrad and Rostov variants, the Gentleman Whist rule is not followed in case 10 contracts are checked and a player who declared the contract doesn't take 10 tricks.

11. When 10 contracts are checked and an AI player declares the contract, he shows his hand before the play and then hides it, despite checking of a 10 contract should be done with open cards of all players.

12. When choosing 'No' within the 'Returnable' option, a whist return is still possible. P.S. The 'Returnable' option, which implies return of the whist on 6 and 7 contracts, is not present in version 2.1, since in modern Russian Preference the 'HalfWhist' and 'Returnable Whist' rules are almost always used together.

13. Regardless of the chosen parameter of the 'Useful Pass' option ('Yes' or 'No'), return of the whist on contracts higher than 7 remains possible. P.S. The title of the option in version 2.1 has been changed to the more familiar denotation for Preference players: 'Pass-Pass-Whist'.

14. When a game is finished (including early exits from a game on the initiative of a user) and a new game is launched (whithout closing the application), the previous game's session of all-pass rounds, if it wasn't interrupted in the last deal of the game, goes on. Thus, if the previous game finished when two or more all-pass rounds had been played before (without exit from the all-pas games' session), the first deal of the new game starts with no possibility of declaring 6 contracts, and if an all-pass game happens in this deal, its value corresponds to the next all-pass game's level (according to the pre-set progression) as compared with the one that had been played last in the previous game. 

--------------------------------------------------------------------------------------------------

Other flaws detected (but not fixed) in version 2.0 are as follows:

1. When choosing 'Exit game' during an all-pass game, the program hangs sometimes, so that the only way to continue playing is to close the application's window and start it again. P.S. It was not possible to identify the bug's reason, as well as exact moments when it happens.

2. When closing the application's window (without using the 'Exit' option), it remains in 'Processes'. Thus, it is recommended to exit from the program using the 'Exit' option of the main menu.

3. It's impossible to finish a play early by offering a resulting number of tricks.

--------------------------------------------------------------------------------------------------

Should you find any other bugs or flaws in the program, please report on them to the email: preference.gixx@mail.ru

--------------------------------------------------------------------------------------------------
