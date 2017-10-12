/*
Copyright (C) 2015-2017 XLAB, Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/


/* Additional JavaScript for ofcloud. */

/**
 * multi_cpu - holds information if the selected flavor is capable of running OpenFOAM in parallel (e.g. flavor has
 * more than 1 VCPU)
 * decompose_dict - defines enabled fields for each decomposition method. This is used for showing only relevant fields
 * when a decomposition method is selected
 * */
horizon.ofcloud = {
    multi_cpu: false,
    decompose_dict: {
        "simple" : "#id_n, #id_delta",
        "hierarchical" : "#id_n, #id_delta, #id_order",
        "scotch" : "#id_strategy, #id_processor_weights",
        "manual" : "#id_datafile"
    }
};

horizon.addInitFunction(horizon.ofcloud.init = function () {
    var $document = $(document);

    function update_decomposition_method_displayed_fields(field) {
        var $this = $(field);
        var decomposition_method = $this.val();

        $this.closest(".form-group").nextAll().hide();
        $(horizon.ofcloud.decompose_dict[decomposition_method]).closest(".form-group").addClass("required").show();
    }

    $document.on('change', '#id_decomposition_method', function () {
        update_decomposition_method_displayed_fields(this);
    });

    $document.on('change', '#id_flavor', function () {
        horizon.ofcloud.cpus = parseInt($('#flavor_vcpus').html());
        horizon.ofcloud.multi_cpu = (horizon.ofcloud.cpus > 1);

        $('#id_subdomains').val(horizon.ofcloud.cpus);
        $('#id_subdomains').closest('.form-group').toggleClass('required', horizon.ofcloud.multi_cpu);
        $('#id_decomposition_method').closest('.form-group').toggleClass('required', horizon.ofcloud.multi_cpu);
        $('.nav.nav-tabs').find('a[href="#add__decompositionaction"]').closest('li').toggleClass('required', horizon.ofcloud.multi_cpu);
    });

    horizon.modals.addModalInitFunction(function (modal) {
        $(modal).find("#id_decomposition_method").change();
    });

    horizon.modals.addModalInitFunction(function (modal) {
        $(modal).find('#id_flavor').change();
    });

    $('#id_flavor').change();
    $('#id_decomposition_method').change();
});