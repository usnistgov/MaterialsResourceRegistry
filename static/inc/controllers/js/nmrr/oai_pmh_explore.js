getRegistries = function(numInstance){
    var values = [];
    $('#id_my_registries input:checked').each(function() {
        values.push(this.value);
    });

    return values;
}