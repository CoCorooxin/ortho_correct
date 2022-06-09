#### ortho_correct

ortho_correct is a spell checker for French language based on levenshstein distance and Peter Norvig generative algorithm that can detect French spelling errors within 2 edit distance.

The user can download the package through the following command line:

$pip install -i https://test.pypi.org/simple/ ortho_correct

Once downloaded, the package can be used as any other python library via 'import ortho_correct'

```python
>>import ortho_correct
#create an instance of the corrector 
>>corrector = ortho_correct.OrthoCorrect() 
#choose the automatic correction mode for your french text
>>corrector.correctionAutomatique("J'aime du cocolate.")
>>"J'aime du chocolate."
#choose the interactif correction mode
>>corrector.correctionAutomatique("J'aime du cocolate.")
>>forme fautive détectée: éternelement
..dans le contexte : désert éternelement gelé
..Veuillez choisir une correction possible : .."éternellement", "not found"
.."éternellement" 
>>"J'aime du chocolate."
#correct a single word in french
>>corrector.corrigeMotAuto("cocolate")
>>"chocolate"
```

ortho_correct includes also a simple and intuitive tokenizer.

```python
>>corrector.tokenizer("Harry aime du chocolate.")
>>["Harry", "aime", "du", "chocolate", "."]
```

