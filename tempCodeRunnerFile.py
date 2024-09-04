def on_row_press(self, instance_table, instance_row):
        row_number = int(instance_row.index/len(instance_table.column_data))
        self.__selected_product = instance_table.row_data[row_number]