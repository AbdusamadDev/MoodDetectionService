import openpyxl
import io


def make_xlsx(data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        (
            "Hodimning ID si",
            "Kamera URL",
            "Xursandchilik",
            "G'amginlik",
            "Jahldorlik",
            "Neytral",
            "Xavotirlik",
            "Hayajon",
            "Behuzur",
            "Kuni",
            "Haftasi",
            "Oyi",
            "Yili",
            "Umumiy sana"
        )
    )
    data = [[str(nano) for nano in micro][1:] for micro in data]
    for row in data:
        ws.append(row)

    output = io.BytesIO()
    wb.save(output)
    output.name = "output.xlsx"
    output.seek(0)

    return output
