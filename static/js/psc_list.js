        var syncList1 = new syncList;
        syncList1.dataList = {
          'psc24':{
              'psc24v10a':'PSC 24V 10A',
              'psc24v40a':'PSC 24V 40A'
          },
          'psc48':{
              'psc48v10a':'PSC 48V 10A',
              'psc48v40a':'PSC 48V 40A'
          },
          'psc24v10a':{
              'wm24v10a':'WeidMuller 24V 7,5A',
              'pw24v5a':'PW 24V 5A'
          },

          'psc24v40a':{
              'wm24v40a':'WeidMuller 24V 40A',
              'mw24v67a':'MeanWell 24V 67A',
          },

          'psc48v10a':{
              'wm48v10a':'WeidMuller 48V 10A',
              'mw48v67a':'MeanWell 48V 67A',
          },

          'psc48v40a':{
              'wm48v20a':'WeidMuller 48V 20A',
              'mw48v67a':'MeanWell 48V 67A',
          }
        };
        syncList1.sync("device_type","device_name","power_supply_type");