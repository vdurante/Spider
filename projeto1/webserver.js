$(document).ready(function() {

  // abas de navegação das máquinas
  $(".nav-tabs").on("click", 'a[role="tab"][class!="add-tab"]', function(e) {
      // ao clicar em uma aba
      e.preventDefault();
      $(this).tab('show');
    })
    .on("click", ".close-tab", function() {
      // ao clicar para fechar uma aba

      // remove a aba
      // remove o conteudo da aba (lista de comandos)
      $($(this).parent().attr('href')).remove();
      $(this).parent().parent().remove();

      // exibe aba 1
      $("a[href=#maquina_1]").tab('show')
    }).after(function() {
      // reordena as abas
      reorder();
    });

  // adicionar abas
  $('.add-tab').on("click", function(e) {
    // ao clicar para adicionar aba
    e.preventDefault();

    // numero de abas (máquinas) abertas
    var id = $(".nav-tabs").children().length;

    // conteúdo da aba da máquina
    // ID da nova máquina é igual ao número de abas existentes (contagem linear 1~K)
    tab_row = '<div class="tab-pane active" id="maquina_' + id + '">' +
      '<div class="row top-buffer">' +
      '<div class="col-lg-1">' +
      '</div>' +
      '<div class="col-lg-2">' +
      '<strong>' +
      'Comando' +
      '</strong>' +
      '</div>' +
      '<div class="col-lg-9">' +
      '<strong>' +
      'Argumentos' +
      '</strong>' +
      '</div>' +
      '</div>' +
      '<hr>' +
      '<div class="row command-row">' +
      '<div class="col-lg-1 text-center">' +
      '</div>' +
      '<div class="col-lg-2">' +
      '<select class="form-control">' +
      '<option>ps</option>' +
      '<option>df</option>' +
      '<option>finger</option>' +
      '<option>uptime</option>' +
      '</select>' +
      '</div>' +
      '<div class="col-lg-9">' +
      '<input type="text" class="form-control" />' +
      '</div>' +
      '</div>' +
      '<div class="row top-buffer">' +
      '<div class="col-lg-1 text-center">' +
      '<button type="button" class="btn btn-success btn-block add-command">+</button>' +
      '</div>' +
      '<div class="col-lg-2">' +
      '</div>' +
      '<div class="col-lg-9">' +
      '</div>' +
      '</div>' +
      '</div>';

    // adiciona aba antes do botão de adicionar
    $(this).closest('li').before('<li><a href="#maquina_' + id + '" count="' + id + '" role="tab"><button class="close close-tab" type="button" >×</button><span>M ' + id + '</span></a></li>');

    // adiciona conteúdo da aba (comandos da máquina)
    $('.tab-content').append(tab_row);

    // exibe a nova máquina adicionada
    $("#myTabs li").eq(-2).children('a').tab('show');
  });

  // adicionar comando
  $('.tab-content').on("click", ".add-command", function() {
    // ao clicar no botão de adicionar comando

    // conteúdo html de um novo comando
    command_row = '<div class="row top-buffer command-row">' +
      '<div class="col-lg-1 text-center">' +
      '<button type="button" class="btn btn-danger btn-block delete-command">X</button>' +
      '</div>' +
      '<div class="col-lg-2">' +
      '<select class="form-control">' +
      '<option>ps</option>' +
      '<option>df</option>' +
      '<option>finger</option>' +
      '<option>uptime</option>' +
      '</select>' +
      '</div>' +
      '<div class="col-lg-9">' +
      '<input type="text" class="form-control" />' +
      '</div>' +
      '</div>';

    // adiciona novo comando antes do botão de adicionar comando (último comando)
    $(this).parent().parent().before(command_row);
  });

  // excluir comando
  $('.tab-content').on("click", ".delete-command", function() {

    // remove o comando - remove a row que envolve o html do comando
    $(this).parent().parent().remove();
  });

  // executar comandos
  $('#run-commands').click(function() {
    // ao clicar no botão de enviar comandos

    // estrutura do objeto que armazenas os comandos das máquinas
    var obj = {
      machines: []
    };

    $(".tab-content div[id^='maquina_']").each(function() {
      // para cada maquina

      // array de comandos auxiliar
      c = []

      $(this).find(".command-row").each(function() {
        // para cada comando dentro desta máquina

        // adiciona comando ao array de comandos auxiliar
        c.push(($(this).find('select')[0].selectedIndex + 1) + " " + $(this).find('input').val());
      });

      // adiciona o array de comandos auxiliar ao array de máquinas
      obj.machines.push({
        commands: c
      });
    });

    // transforma em json
    json = JSON.stringify(obj);

    // insere json em uma FORM invisível
    $("#json-input").val(json);

    // envia form ao servidor
    $("#json-form").submit();
  });

  // reordenar máquinas após a exclusão de alguma delas
  function reorder() {
    // contador de máquinas
    count = 1;
    $("#MyTabs li a[href^='#maquina_']").each(function() {
      // para cada máquina existente,
      // atualiza os valores referentes à máquina com o novo valor da contagem de máquinas
      id = $(this).attr('count');
      $('#maquina_' + id).attr('id', 'maquina_' + count);
      $(this).attr('href', '#maquina_' + count);
      $(this).attr('count', count);
      $(this).children('span').html('M ' + count);
      count++;
    });
  }
});
