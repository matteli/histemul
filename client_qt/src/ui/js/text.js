function getText(val) {
    if (val[0] == 20001)
    {
        return ([qsTr("%1 declares you the war").arg(model.getName("Country",val[1]))
                 ,"desc"
                 ,[qsTr("ok")]]);
    }

    else if (val[0] == 1)
    {
        return(["titre",
               "description",
               "ok"]);
    }
}
