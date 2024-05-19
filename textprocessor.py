import os
from transformers import pipeline


classifier = pipeline(
    "ner",
    model=f"{os.getcwd()}\\TokenClassifierModel",
    tokenizer=f"{os.getcwd()}\\TokenClassifierModel"
)


def classify_text(text):
    return bool(classifier(text))


if __name__ == "__main__":
    a = classify_text("Машинист поезда (номер поезда назвать) на 3-ем пути станции Заливное. Машинист поезда «__» на 3-м пути станции Заливное, Глошев. Слушаю вас. Машинист поезда «__» Подтянули вплотную к сигналу Н-3? ТЧМ	ДНЦ	Да, вплотную встали. Перекрывайте сигнал Н-3. Машинист Глошев. Понятно, перекрываю сигнал Н-3 ТЧМ	ДНЦ	Прибытие 8:34 Понятно. Прибытие 8:34")
    print(a)